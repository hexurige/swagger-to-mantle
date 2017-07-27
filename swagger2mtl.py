import re


class Column(object):
    def __init__(self, name, type_name, optional):
        self.name = name
        self.typeName = type_name
        self.optional = optional
        self.fieldName = self.get_field_name()

    def __str__(self):
        rtr = 'Column Name: ' + self.name + '\n'
        rtr += 'Type Name: ' + self.typeName + '\n'
        rtr += 'Optional: ' + self.optional + '\n'
        return rtr

    def get_field_name(self):
        formatted_field_name = ''
        name_words = str.split(self.name, '_')
        for idx, word in enumerate(name_words):
            if idx == 0:
                formatted_field_name = formatted_field_name + word
            else:
                formatted_field_name = formatted_field_name + word.title()
        return formatted_field_name


def delete_content(pfile):
    pfile.seek(0)
    pfile.truncate()

model_list = []
mtl_json_f = open('mtlJson', 'w')
mtl_header_f = open('mtlHeader', 'w')
delete_content(mtl_json_f)
delete_content(mtl_header_f)

with open('input') as f:
    lines = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
lines = [x.strip() for x in lines]

print('### reading input..')
print(lines)
print('### construct models..')


for line in lines:
    line_properties = re.findall(r"[\w']+", line)
    name = line_properties[0]
    type_name = line_properties[1]
    optional = line_properties[2]
    model = Column(name, type_name, optional)
    model_list.append(model)

print('### write mtl json')

# write mapping dictionary
mtl_json_f.write('+(NSDictionary*)JSONKeyPathsByPropertyKey{\n')
mtl_json_f.write('\treturn @{\n')
for model in model_list:
    formatted_field_string = '\t\t@"%s" : @"%s",\n' % (model.fieldName, model.name)
    mtl_json_f.write(formatted_field_string)
mtl_json_f.write('\t};\n')
mtl_json_f.write('}\n\n')

# write Int32 null checking.
mtl_json_f.write('#pragma Int32 check nil.\n')
for model in model_list:
    if model.typeName == 'Int32':
        mtl_json_f.write('+(NSValueTransformer *)%sJSONTransformer{\n' % model.fieldName)
        mtl_json_f.write('\treturn [MTLValueTransformer transformerWithBlock:^id(id inObj) {\n')
        mtl_json_f.write('\t\tif (inObj == nil) {\n')
        mtl_json_f.write('\t\t\treturn [NSNumber numberWithInteger:0];\n')
        mtl_json_f.write('\t\t} else {\n')
        mtl_json_f.write('\t\t\treturn inObj;\n')
        mtl_json_f.write('\t\t}\n')
        mtl_json_f.write('\t}];\n')
        mtl_json_f.write('}\n\n')

# write Decimal null checking.
mtl_json_f.write('#pragma Decimal check nil.\n')
for model in model_list:
    if model.typeName == 'Decimal':
        mtl_json_f.write('+(NSValueTransformer *)%sJSONTransformer{\n' % model.fieldName)
        mtl_json_f.write('\treturn [MTLValueTransformer transformerWithBlock:^id(id inObj) {\n')
        mtl_json_f.write('\t\tif (inObj == nil) {\n')
        mtl_json_f.write('\t\t\treturn [NSNumber numberWithDouble:0.0f];\n')
        mtl_json_f.write('\t\t} else {\n')
        mtl_json_f.write('\t\t\treturn inObj;\n')
        mtl_json_f.write('\t\t}\n')
        mtl_json_f.write('\t}];\n')
        mtl_json_f.write('}\n\n')

# write Boolean null checking.
mtl_json_f.write('#pragma Boolean check nil.\n')
for model in model_list:
    if model.typeName == 'Boolean':
        mtl_json_f.write('+(NSValueTransformer *)%sJSONTransformer{\n' % model.fieldName)
        mtl_json_f.write('\treturn [MTLValueTransformer transformerWithBlock:^id(id inObj) {\n')
        mtl_json_f.write('\t\tif (inObj == nil) {\n')
        mtl_json_f.write('\t\t\treturn [NSNumber numberWithInteger:0];\n')
        mtl_json_f.write('\t\t} else {\n')
        mtl_json_f.write('\t\t\treturn inObj;\n')
        mtl_json_f.write('\t\t}\n')
        mtl_json_f.write('\t}];\n')
        mtl_json_f.write('}\n\n')

mtl_json_f.close()

print('### write mtl header')
for model in model_list:
    formatted_field_string = ''
    if model.typeName == 'Int32':
        formatted_field_string = '@property(nonatomic) int %s;\n' % model.fieldName
    elif model.typeName == 'Decimal':
        formatted_field_string = '@property(nonatomic) double %s;\n' % model.fieldName
    elif model.typeName == 'Boolean':
        formatted_field_string = '@property(nonatomic) BOOL %s;\n' % model.fieldName
    elif model.typeName == 'String':
        formatted_field_string = '@property(nonatomic, copy) NSString *%s;\n' % model.fieldName
    elif model.typeName == 'DateTime':
        formatted_field_string = '@property(nonatomic, copy) NSString *%s;\n' % model.fieldName
    else:
        print(model.typeName)
        formatted_field_string = '#TODO *%s;\n' % model.fieldName

    mtl_header_f.write(formatted_field_string)

mtl_header_f.close()