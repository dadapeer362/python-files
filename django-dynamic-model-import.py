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
    
    default_values = default_value_mapping.get(table_name, {})

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
        default_value = default_values.get(field_name)

        if field_name == 'id':
            continue
        if field_name == 'created_at':
            field_kwargs.update({'auto_now_add': True})
        if field_name == 'updated_at':
            field_kwargs.update({'auto_now': True})
        if field_name == 'is_active':
            field_kwargs.update({'default': True})
        if default_value is not None:
            field_kwargs.update({'default': default_value})

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
        elif field_type.startswith('double precision'):
            field_class = models.FloatField
        elif field_type.startswith('numeric') or field_type.startswith('real'):
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


default_value_mapping = {
    'student_fee_dues': {
        'amount_paid': 0,
        'payment_completed': False,
    },
    'student_accounts': {
        'excess_payment': 0,
        'total_fee_pending': 0,
        'total_penalty_pending': 0,
        'total_waiver': 0,
    },
    'student_balance_logs': {
        'amount': 0,
    },
    'student_refunds': {
        'amount': 0,
    },
    'student_waivers': {
        'amount': 0,
    },
    'student_penalities': {
        'amount': 0,
        'paid_amount': 0,
        'is_paid': False,
    },
}

StudentProfile = generate_model_from_db_table('student_profiles')
StudentFeeDue = generate_model_from_db_table('student_fee_dues')
StudentAccount = generate_model_from_db_table('student_accounts')
StudentBalanceLog = generate_model_from_db_table('student_balance_logs')
StudentRefund = generate_model_from_db_table('student_refunds')
StudentWaiver = generate_model_from_db_table('student_waivers')
StudentPenalty = generate_model_from_db_table('student_penalities')
InstituteCourse = generate_model_from_db_table('institute_courses')
InstituteClass = generate_model_from_db_table('institute_classes')
InstituteFeeStucture = generate_model_from_db_table('institute_fee_structures')
