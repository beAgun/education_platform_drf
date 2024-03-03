from django.db.models import Count, Q, Case, DateTimeField, When, Value, BooleanField, Avg, F, FloatField, Func
from django.db.models.functions import Coalesce, Concat, Cast
from django.forms import model_to_dict
from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from rest_framework import generics, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from users.models import User
from .models import *
from .permissions import *
from .serializers import *


# viewsets.ModelViewSet
class ProductViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        products = (
            Product.objects.annotate(
                lessons=Count('lesson', distinct=True),

            )
            #.filter(start_date__gt=timezone.now())
            #.filter(Q(author_id=self.request.user.id) |
            #        ~Q(enrollment__student_id=self.request.user.id, enrollment__permission=True))
            .order_by('title')
        )

        result = products.values('title', 'price', 'start_date',
                                 'lessons', 'author__username', )
        return result

    @action(methods=['get'], detail=True, permission_classes=(IsAcceptedStudentOrIsAuthor, ))
    def lessons(self, request, pk):
        self.get_object()
        pr = get_object_or_404(Product, id=self.kwargs['pk'])
        lessons = pr.lesson_set.all()
        return Response({'lessons': ProductLessonSerializer(lessons, many=True).data})


# class ProductLessonView(generics.ListAPIView):
#     serializer_class = ProductLessonSerializer
#     permission_classes = (IsAcceptedStudentOrIsAuthor, )
#
#     def get_queryset(self):
#         pr = get_object_or_404(Product, id=self.kwargs['pk'])
#         return pr.lesson_set.all()


class ProductAPICreateUpdate(mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = (IsTutor, IsAuthorOrReadOnly)

    # def get_queryset(self):
    #     if self.request.method == 'POST':
    #         queryset = get_object_or_404(Product.objects.filter(author_id=self.request.user.pk), pk=self.kwargs['pk'])
    #     else:
    #         queryset = Product.objects.all()
    #     return queryset


class CreateUserView(CreateAPIView):
    model = get_user_model()
    queryset = model.objects.all()
    permission_classes = (IsAnonymousUser, )
    serializer_class = UserSerializer


class GetAccess2(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):

        # Получаем продукт
        pr = get_object_or_404(Product, id=self.kwargs['pk'])

        # Даём студенту разрешение на доступ к курсу
        q = Enrollment.objects.filter(student=request.user, product=pr)
        if q.exists():
            if q[0].permission is True:
                return Response({'error': 'У вас уже есть доступ!'})
            enrollment = q.update(permission=True, is_reserved=True)
        else:
            enrollment = Enrollment.objects.create(student=request.user, product=pr,
                                                   permission=True, is_reserved=True)

        # Собираем всех студентов курса по их id
        students_id = [i['id'] for i in pr.students.filter(enrollment__permission=True).order_by('enrollment__date').values('id')]  # pr.students.count()
        n, a, b, rule = len(students_id), pr.min_group_students_qty, pr.max_group_students_qty, pr.rule

        if pr.start_date <= timezone.now():
            new_students = [request.user.id]
            q = Group.objects.filter(product=pr, is_full=False)
            if q:
                group = q[0]
                group.students = list(set(group.students).union(new_students))
                group.save()
                # group.objects.update(students=group.students + new_students)
            else:
                group = Group.objects.create(title='group', product=pr,
                                             reserved_group=True, is_full=False,
                                             students=new_students)
                group.title = f'group_{group.id}'
                group.save()

            if a == len(group.students):
                group.reserved_group = False
                group.save()
            if b == len(group.students):
                group.is_full = True
                group.save()

            if group.reserved_group is False:
                enrollments = Enrollment.objects.filter(student_id__in=group.students)
                for enr in enrollments:
                    enr.is_reserved = False
                    enr.save()

            return Response({'status': 'ok'})

        else:
            # Начинаем формировать группы заново
            groups = []
            # Создадим переменную для запоминания id группы, в которой окажется текущий пользователь
            user_group_id = 0
            # Берём id последней группы
            last_gr = Group.objects.order_by('-id').first()
            last_id = 1
            if last_gr:
                last_id = last_gr.id

            # Если участников курса меньше минимума для формирования группы, они отправляются в резервную
            if n < a:
                if request.user.id in students_id:
                    user_group_id = last_id + 1
                groups += [{'students': students_id, 'is_full': False,
                            'reserved_group': True, 'product': pk,
                            'id': last_id + 1, 'title': f'group_{last_id + 1}'}]

            # Иначе сначала сформируем группы с минимальным количеством участников и распределим оставшихся студентов по
            # ним, чтобы никто не оказался в запасе, хотя мог бы быть в группе
            else:
                i, j = 0, a
                for k in range(n // a):
                    last_id += 1
                    # не забываем запомнить id группы текущего студента
                    sts = students_id[i:j]
                    if request.user.id in sts:
                        user_group_id = last_id
                    groups += [{'students': sts, 'is_full': False,
                                'reserved_group': False, 'product': pk,
                                'id': last_id, 'title': f'group_{last_id}'}]
                    if a == b:
                        groups[-1]['is_full'] = True
                    i += a; j += a

                # Распределяем остаток студентов
                rest_students = students_id[j - a:n]
                m = len(rest_students)
                i, j = 0, 0
                while j < m:
                    if i >= len(groups):
                        i = 0
                    if len(groups[i]['students']) == b:
                        break

                    # Если правило распределения по умолчанию, то заполняем группы до максимума
                    if rule:
                        sts = rest_students[j:j + b - a]
                        if request.user.id in sts:
                            user_group_id = last_id
                        groups[i]['students'] += sts
                        groups[i]['is_full'] = True
                        j += (b - a)

                    # Иначе последовательно в группы добавляем по одному студенту
                    else:
                        sts = [rest_students[j]]
                        if request.user.id in sts:
                            user_group_id = last_id
                        groups[i]['students'] += sts
                        if len(groups[i]['students']) == b:
                            groups[i]['is_full'] = True
                        j += 1
                    i += 1

                # Все оставшиеся попадают в запас
                if j < m:
                    sts = rest_students[j - b + a:] if rule else [rest_students[j]]
                    if request.user.id in sts:
                        user_group_id = last_id + 1
                    groups += [{'students': sts, 'is_full': False,
                                'reserved_group': True, 'product': pk,
                                'id': last_id + 1, 'title': f'group_{last_id + 1}'}]

            # if n // a * (b - a) >= n % a:

            # Теперь заполняем информацию о том, в запасе ли или нет каждый студент на данном курсе
            if groups[-1]['reserved_group']:
                Enrollment.objects.filter(product_id=pk).update(
                    is_reserved=Case(When(student_id__in=groups[-1]['students'], then=Value(True)),
                                     default=Value(False), output_field=BooleanField()))

            # Удаляем все старые группы по курсу из базы и добавляем новые
            Group.objects.filter(product_id=pk).delete()
            serializer = GroupSerializer(data=groups, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Получаем информацию о группе, в которой находится текущий пользователь,
            # чтобы вернуть ему эти данные в качестве ответа
            user_group = {}
            if user_group_id:
                user_group = model_to_dict(Group.objects.get(id=user_group_id))
                user_group['students'] = list(User.objects.filter(id__in=user_group['students']).values('username'))

            return Response({'user_group': user_group})


class ProductStatisticsList(generics.ListAPIView):
    serializer_class = ProductStatisticsSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        # queryset = Product.objects.annotate(
        #     num_students=Count('enrollment__student_id'),
        #     occupancy=Func(F('group__students'), function='CARDINALITY'),
        #     #occupancy=Avg(F('group__students__length') / F('group__students__length__max'), output_field=FloatField()) * 100,
        #     acquisition=Cast(Count('enrollment') / User.objects.filter(status=False).count(), FloatField()) * 100
        # ).values(
        #     'title',
        #     'start_date',
        #     'num_students',
        #     'occupancy',
        #     'acquisition',
        #     'id'
        # ).order_by('title')
        queryset = Product.objects.raw('''select 
                                            p.id,
                                            p.title, 
                                            start_date,
                                            count(e.student_id) as num_students,
                                            round(iif(stat.x, stat.x, 0), 2) as occupancy,
                                            round(cast(count(e.id) as real)/
                                                  cast((select 
                                                            count(*) 
                                                        from users_user u) 
                                                  as real) * 100, 2) as acquisition
                                        from 
                                            edu_product p
                                            left join edu_enrollment e on e.product_id = p.id and e.permission is True
                                            left join (select 
                                                      p.id, count(*), 
                                                      avg(json_array_length(g.students))/
                                                      max(json_array_length(g.students)) * 100 as x
                                                  from edu_group g join edu_product p on p.id = g.product_id
                                                  group by p.id) stat on stat.id = p.id
                                        group by p.id
                                        order by 1''')

        return queryset


