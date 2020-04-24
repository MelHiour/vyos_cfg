def filter_list(raw_list, exclude_list):
    filtered_list = []
    for item in raw_list:
        print('ITEM: {}'.format(item))
        for keyword in exclude_list:
            print('KEYWORD: {}'.format(keyword))
            if keyword in item:
                print('Keywoard in item!')
                break
        else:
            print('Appending {}'.format(item))
            filtered_list.append(item)
    unique_list = []
    for item in filtered_list:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list

raw_list = ['blah', 'what', 'the', 'fuck']
exclusion = ['the', 'fuck']

result = filter_list(raw_list, exclusion)

print(result)

