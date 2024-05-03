from django.db import models
from django.db import connections


def generate_model_from_db_table(table_name):
    with connections['leo1fees'].cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
        """)
        table_description = cursor.fetchall()

    class Meta:
        managed = False
        db_table = table_name

    attrs = {'Meta': Meta, '__module__': 'cardFeeBridge'}
    for field_info in table_description:
        field_name = field_info[0]
        field_type = field_info[1]
        field_max_length = field_info[2] or 1000
        field_nullable = field_info[3] == 'YES'
        field_kwargs = {'null': field_nullable}

        if field_name == 'id':
            continue

        # Convert database field types to Django field types
        if field_type.startswith('character'):
            field_class = models.CharField
            field_kwargs.update({'max_length': field_max_length})
        elif field_type.startswith('integer'):
            field_class = models.IntegerField
        elif field_type.startswith('timestamp'):
            field_class = models.DateTimeField
        elif field_type == 'boolean':
            field_class = models.BooleanField
        elif field_type == 'json':
            field_class = models.JSONField
        elif field_type.startswith('numeric') or field_type.startswith('double precision') or field_type.startswith('real'):
            field_class = models.DecimalField
        elif field_type == 'text':
            field_class = models.TextField
        elif field_type == 'inet' or field_type == 'bytea' or field_type == 'uuid':
            field_class = models.CharField
            field_kwargs.update({'max_length': 39})
        else:
            field_class = models.CharField
            field_kwargs.update({'max_length': field_max_length})

        # Add field to attributes
        attrs[field_name] = field_class(**field_kwargs)

    # Create the model dynamically
    model_class = type(table_name.capitalize(), (models.Model,), attrs)
    return model_class


InstituteCourse = generate_model_from_db_table('institute_courses')
InstituteClass = generate_model_from_db_table('institute_classes')
