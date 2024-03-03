def f(students_id, n, a, b):
    groups = []
    id = 2
    rule = False

    if n < a:
        groups += [{'students': students_id, 'is_full': False, 'reserved_group': True, 'product_id': id}]
        return groups

    i, j = 0, a
    for k in range(n // a):
        groups += [{'students': students_id[i:j], 'is_full': False, 'reserved_group': False, 'product_id': id}]
        i += a; j += a

    rest_students = students_id[j - a:n]
    m = len(rest_students)
    i, j = 0, 0
    while j < m:
        if i >= len(groups):
            i = 0
        if len(groups[i]['students']) == b:
            break

        if not rule:
            groups[i]['students'] += [rest_students[j]]
            j += 1
        else:
            groups[i]['students'] += rest_students[j:j + b - a]
            j += (b - a)
        i += 1

    if j < m:
        groups += [{'students': [rest_students[j]] if not rule else rest_students[j - b + a:], 'is_full': False, 'reserved_group': True, 'product_id': id}]

    return groups


def test(f):
    students_id = []
    for i in range(30):
        students_id += [i]
        print('*'*50)
        print(students_id)
        js = f(students_id, len(students_id), 3, 4)
        print('groups', len(js), ': ', end='')
        for gr in js:
            print(gr['students'], end='   ')
        print()


def main():
    n = int(input())
    students_id = []
    for i in range(n):
        students_id += [i]
    print('*' * 50)
    print(students_id)
    js = f(students_id, len(students_id), 3, 4)
    print('groups', len(js), ': ', end='')
    for gr in js:
        print(gr['students'], end='   ')
    print()


if __name__ == '__main__':
    main()
    #test(f)