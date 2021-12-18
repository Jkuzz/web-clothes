import csv
import json
import datetime


def db_add_item(form_data):
    if not validate_form_response(form_data):
        return None, "Invalid input"
    line_to_save = make_item_line(form_data)
    save_line_to_db(line_to_save, 'items.csv')
    return None, None


def check_id_exists(item_id):
    with open('items.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        id_index = header.index('Id')
        for row in csv_reader:
            if row[id_index] == item_id:
                return True
    return False


def validate_use_form(form_data):
    required = ['id', 'day']
    for r_field in required:
        if r_field not in form_data.keys() or not form_data[r_field]:
            return False

    if form_data['day'] not in ['today', 'yesterday', 'custom']:
        return False

    if form_data['day'] == 'custom':
        if 'date' not in form_data.keys() or not form_data['date']:
            return False
        try:
            datetime.datetime.strptime(form_data['date'], '%Y-%m-%d')
        except ValueError:
            return False

    return True


def db_add_use(form_data):
    print(form_data)
    if not validate_use_form(form_data):
        return None, 'Invalid request'
    item_id = form_data['id']
    use_day = form_data['day']

    if use_day == 'custom':
        use_date = form_data['date']
    else:
        date_to_print = datetime.date.today()
        if use_day == 'yesterday':
            date_to_print -= datetime.timedelta(days=1)
        use_date = date_to_print.strftime('%Y-%m-%d')
    line = [item_id, use_date]

    save_line_to_db(line, 'item_uses.csv')
    return None, None


def save_line_to_db(line, target_file):
    with open(target_file, 'a', encoding='utf-8', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(line)


def make_item_line(form_data):
    styles = [form_data[field] for field in form_data if field.startswith('style')]
    item_style = ", ".join(styles)
    if form_data['id']:
        item_id = form_data['id']
    else:
        item_id = db_find_free_id()
    fields = [
        item_id, form_data['type'], form_data['name'],
        item_style, form_data['colour'], form_data['comfy'],
        0, form_data['mend'], form_data['state']
    ]
    return fields


def validate_form_response(form_data):
    required_exist = [
        'type', 'name', 'colour',
        'comfy', 'mend', 'state'
    ]
    required_filled = [
        'type', 'name', 'colour'
    ]
    unique_types, unique_styles = db_get_unique_types_styles()
    print(form_data)

    # All must be present, even if null
    for check_existence in required_exist:
        if check_existence not in form_data.keys():
            return False, 'Missing form fields'

    for field in form_data:
        # Required fields must be filled
        if field in required_filled:
            if field == '':
                return False, 'Missing required fields'
        # Styles must exist
        if field == 'item_type':
            if form_data[field] not in unique_types:
                return False, 'Invalid item type'
        elif field.startswith('style'):
            if form_data[field] not in unique_styles:
                return False, 'Invalid style'

    return True, 'Ok'


def db_find_free_id():
    lowest = 0
    with open('items.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        if 'Id' not in header:
            return None
        id_index = header.index('Id')
        for row in csv_reader:
            if not row:
                continue
            if int(row[id_index]) > lowest:
                lowest = int(row[id_index])
    return lowest + 1


def db_get_unique_types_styles(json_response=False):
    styles = set()  # a set only keeps unique values
    types = set()
    with open('items.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        style_index = header.index('Style')
        type_index = header.index('Type')
        for row in csv_reader:
            if not row:
                continue
            types.add(row[type_index])
            for style in row[style_index].split(', '):
                styles.add(style)

    if json_response:
        response = json.dumps({
            'types': list(types),
            'styles': list(styles)
            }
        )
        return response
    else:
        return list(types), list(styles)


def db_edit_item(form_data):
    if not form_data['id']:  # Id is not in validate func
        return None, 'Id not provided'
    form_valid, error_message = validate_form_response(form_data)
    if not form_valid:
        return None, error_message

    edited_rows = []
    edited = False
    with open('items.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        id_index = header.index('Id')
        for row in csv_reader:
            if row[id_index] == form_data['id']:
                new_line = make_item_line(form_data)
                edited_rows.append(new_line)
                edited = True
            else:
                edited_rows.append(row)

    if not edited:
        return None, "Id doesn't exist"

    with open('items.csv', 'w', encoding='utf-8', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(header)
        for row in edited_rows:
            csv_writer.writerow(row)

    return None, None


def item_to_dict(header, item_row):
    item_dict = {}
    for i, field_name in enumerate(header):
        item_dict[field_name] = item_row[i]
    return item_dict


def db_find_item(id_to_find):
    print(f'Looking for id: {id_to_find}')
    with open('items.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        id_index = header.index('Id')
        for row in csv_reader:
            if int(row[id_index]) == int(id_to_find):
                return item_to_dict(header, row)
    return None


def db_get_item_uses(item_id):
    uses = []
    with open('item_uses.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        id_index = header.index('Id')
        date_index = header.index('Date')
        for row in csv_reader:
            if int(row[id_index]) == int(item_id):
                uses.append(row[date_index])
    return uses


def db_get_items():
    items = []
    with open('items.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader)
        for row in csv_reader:
            new_item = {}
            for i, field in enumerate(row):
                new_item[header[i]] = field
            items.append(new_item)

    return items

