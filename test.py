def is_even(numb: int):
    return not numb & 1  # bitwise operation


def get_list(max: int):
    """return all odd number from 0 to max"""
    list: list[int] = []
    for i in range(max + 1):  # off by one error
        if not is_even(i):
            list.append(i)
    return list


def remove_each(list: list[int], step: int, start_at: int):
    number_to_remove: list[int] = []

    for i in range(-1, len(list), step):  # -1 off by one error
        if i < 0:
            continue

        number = list[i]
        if number <= start_at:
            continue

        number_to_remove.append(list[i])

    for number in number_to_remove:
        list.remove(number)


nombre_chanceux: list[int] = get_list(1000)

for i in range(1, len(nombre_chanceux)):
    number = nombre_chanceux[i]
    print(i, number)

    if number > len(nombre_chanceux):
        break

    remove_each(nombre_chanceux, number, number)

print(nombre_chanceux)
