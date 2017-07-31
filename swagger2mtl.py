# ====
# Swagger Class
# Created by xhe585, on 28/Jul/2017.
# ====
import json
import os
import time
import sys
import requests


class Swagger(object):
    """Swagger"""

    def __init__(self, j):
        self.__dict__ = j
        self.host = self.host
        self.models = []
        for definition in self.definitions:
            self.models.append(Model(self.definitions[definition]))

    def __str__(self):
        rtr = ''
        for m in self.models:
            rtr += m.__str__()

        return rtr

    def create_mantles_directory(self):
        if not os.path.exists('mantles'):
            os.makedirs('mantles')

    def create_mantles(self):
        self.create_mantles_directory()

        for model in self.models:
            model.create_header_file()
            model.create_implement_file()


class Model(object):
    """Model"""

    def __init__(self, dict):
        self.__dict__ = dict
        self._properties = []
        self.file_name = 'AFM{0}'.format(self.title)
        self.mantle_path = 'mantles'
        for p in self.properties:
            self._properties.append(Property(self.properties[p]))

    def __str__(self):
        rtr = 'Model Title: {0} | Type: {1} | Number of Properties: {2}\n'.format(self.title, self.type, len(self._properties))
        return rtr

    def get_comment(self, is_header):
        if not os.path.exists('comment'):
            return ''
        else:
            rtr = '//\n'
            if is_header:
                rtr += '//  {0}.h\n'.format(self.file_name)
            else:
                rtr += '//  {0}.m\n'.format(self.file_name)

            with open('comment') as f:
                lines = f.readlines()
                for line in lines:
                    rtr += line
            
            rtr += '//  On {0}\n'.format(time.strftime("%d/%m/%Y"))
            rtr += '//\n'
            return rtr

    def create_header_file(self):
        file_name = '{0}.h'.format(self.file_name)
        f = open(os.path.join(self.mantle_path, file_name), 'w')
        f.write(self.get_header_file_content())
        f.close()

    def create_implement_file(self):
        file_name = '{0}.m'.format(self.file_name)
        f = open(os.path.join(self.mantle_path, file_name), 'w')
        f.write(self.get_implement_file_content())
        f.close()


    def get_JSONKeyPathsByPropertyKey_method(self):
        rtr = ''
        rtr += '+(NSDictionary*)JSONKeyPathsByPropertyKey{\n'
        rtr += '\treturn @{\n'
        for p in self._properties:
            rtr += '\t\t@"{0}" : @"{1}",\n'.format(p.get_field_name(), p.title)
                
        rtr += '\t};\n'
        rtr += '}\n\n'
        return rtr

    def get_header_file_content(self):
        rtr = self.get_comment(True)
        rtr += '#import <Mantle/Mantle.h>\n\n'
        rtr += '@interface {0} : MTLModel <MTLJSONSerializing>\n\n'.format(self.file_name)
        for p in self._properties:
            rtr += p.get_property_header()
        rtr += '\n@end\n'
        return rtr

    def get_implement_file_content(self):
        rtr = self.get_comment(False)
        rtr += '#import "{0}.h"\n\n'.format(self.file_name)
        rtr += '@implementation {0}\n\n'.format(self.file_name)
        rtr += self.get_JSONKeyPathsByPropertyKey_method()
        for p in self._properties:
            rtr += p.get_null_checking_funtion()
        rtr += '\n@end\n'
        return rtr

class Property(object):
    """Property"""

    def __init__(self, dict):
        self.__dict__ = dict

    def __str__(self):
        rtr = ''
        return rtr

    def get_field_name(self):
        formatted_field_name = ''
        name_words = str.split(self.title, '_')
        for idx, word in enumerate(name_words):
            if idx == 0:
                formatted_field_name = formatted_field_name + word
            else:
                formatted_field_name = formatted_field_name + word.title()
        return formatted_field_name

    def get_property_header(self):
        header = ''
        if self.type == 'Int32':
            header = '@property(nonatomic) int %s;\n' % self.get_field_name()
        elif self.type == 'Decimal':
            header = '@property(nonatomic) double %s;\n' % self.get_field_name(
            )
        elif self.type == 'Boolean':
            header = '@property(nonatomic) BOOL %s;\n' % self.get_field_name()
        elif self.type == 'String':
            header = '@property(nonatomic, copy) NSString *%s;\n' % self.get_field_name()
        elif self.type == 'DateTime':
            header = '@property(nonatomic, copy) NSString *%s;\n' % self.get_field_name()
        else:
            pass
        return header

    def get_null_checking_funtion(self):
        # write Int32 null checking.
        rtr = ''

        if self.type == 'Int32':
            rtr += '+(NSValueTransformer *)%sJSONTransformer{\n' % self.get_field_name()
            rtr += '\treturn [MTLValueTransformer transformerWithBlock:^id(id inObj) {\n'
            rtr += '\t\tif (inObj == nil) {\n'
            rtr += '\t\t\treturn [NSNumber numberWithInteger:0];\n'
            rtr += '\t\t} else {\n'
            rtr += '\t\t\treturn inObj;\n'
            rtr += '\t\t}\n'
            rtr += '\t}];\n'
            rtr += '}\n\n'

        elif self.type == 'Decimal':
            rtr += '+(NSValueTransformer *)%sJSONTransformer{\n' % self.get_field_name()
            rtr += '\treturn [MTLValueTransformer transformerWithBlock:^id(id inObj) {\n'
            rtr += '\t\tif (inObj == nil) {\n'
            rtr += '\t\t\treturn [NSNumber numberWithDouble:0.0f];\n'
            rtr += '\t\t} else {\n'
            rtr += '\t\t\treturn inObj;\n'
            rtr += '\t\t}\n'
            rtr += '\t}];\n'
            rtr += '}\n\n'

        elif self.type == 'Boolean':
            rtr += '+(NSValueTransformer *)%sJSONTransformer{\n' % self.get_field_name()
            rtr += '\treturn [MTLValueTransformer transformerWithBlock:^id(id inObj) {\n'
            rtr += '\t\tif (inObj == nil) {\n'
            rtr += '\t\t\treturn [NSNumber numberWithInteger:0];\n'
            rtr += '\t\t} else {\n'
            rtr += '\t\t\treturn inObj;\n'
            rtr += '\t\t}\n'
            rtr += '\t}];\n'
            rtr += '}\n\n'

        return rtr

#============================ *** Main *** ============================

def main(argv):
    if len(argv) <= 1:
        print('python3 swagger2mtl.py YOUR-URL')
        return

    link = argv[1]
    print('Reading Url: {0}'.format(link))
    request = requests.get(link)
    swagger_json = request.json()
    
    swagger = Swagger(swagger_json)
    swagger.create_mantles()

if __name__ == "__main__":
    main(sys.argv)