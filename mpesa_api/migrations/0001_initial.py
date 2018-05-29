from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access_token', models.CharField(max_length=40)),
                ('type', models.CharField(max_length=3)),
                ('expires_in', models.BigIntegerField()),
            ],
            options={
                'db_table': 'tbl_access_token',
            },
        ),
        migrations.CreateModel(
            name='B2CRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.BigIntegerField()),
                ('amount', models.DecimalField(max_digits=20, decimal_places=2)),
                ('conversation_id', models.CharField(max_length=40, null=True, blank=True)),
                ('originator_conversation_id', models.CharField(max_length=40, null=True, blank=True)),
                ('response_code', models.CharField(max_length=5, null=True, blank=True)),
                ('response_description', models.TextField(null=True, blank=True)),
                ('request_id', models.CharField(max_length=20, null=True, blank=True)),
                ('error_code', models.CharField(max_length=20, null=True, blank=True)),
                ('error_message', models.TextField(null=True, blank=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tbl_b2c_requests',
                'verbose_name_plural': 'B2C Requests',
            },
        ),
        migrations.CreateModel(
            name='B2CResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.BigIntegerField(null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('conversation_id', models.CharField(max_length=40, null=True, blank=True)),
                ('originator_conversation_id', models.CharField(max_length=40, null=True, blank=True)),
                ('result_type', models.CharField(max_length=5, null=True, blank=True)),
                ('result_code', models.CharField(max_length=5, null=True, blank=True)),
                ('result_description', models.TextField(null=True, blank=True)),
                ('transaction_id', models.CharField(max_length=20, null=True, blank=True)),
                ('transaction_receipt', models.CharField(max_length=20, null=True, blank=True)),
                ('transaction_amount', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('working_funds', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('utility_funds', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('paid_account_funds', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('transaction_date', models.DateTimeField(null=True, blank=True)),
                ('mpesa_user_name', models.CharField(max_length=100, null=True, blank=True)),
                ('is_registered_customer', models.CharField(max_length=1, null=True, blank=True)),
            ],
            options={
                'db_table': 'tbl_b2c_response',
                'verbose_name_plural': 'B2C Responses',
            },
        ),
        migrations.CreateModel(
            name='C2BRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('transaction_type', models.CharField(max_length=20, null=True, blank=True)),
                ('transaction_id', models.CharField(unique=True, max_length=20)),
                ('transaction_date', models.DateTimeField(null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('business_short_code', models.CharField(max_length=20, null=True, blank=True)),
                ('bill_ref_number', models.CharField(max_length=50, null=True, blank=True)),
                ('invoice_number', models.CharField(max_length=50, null=True, blank=True)),
                ('org_account_balance', models.DecimalField(default=0.0, null=True, max_digits=20, decimal_places=2, blank=True)),
                ('third_party_trans_id', models.CharField(max_length=50, null=True, blank=True)),
                ('phone', models.BigIntegerField(null=True, blank=True)),
                ('first_name', models.CharField(max_length=50, null=True, blank=True)),
                ('middle_name', models.CharField(max_length=50, null=True, blank=True)),
                ('last_name', models.CharField(max_length=50, null=True, blank=True)),
                ('is_validated', models.BooleanField(default=False)),
                ('is_completed', models.BooleanField(default=False)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tbl_c2b_requests',
                'verbose_name_plural': 'C2B Requests',
            },
        ),
        migrations.CreateModel(
            name='OnlineCheckout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.BigIntegerField()),
                ('amount', models.DecimalField(max_digits=20, decimal_places=2)),
                ('checkout_request_id', models.CharField(default=b'', max_length=50)),
                ('account_reference', models.CharField(default=b'', max_length=50)),
                ('transaction_description', models.CharField(max_length=50, null=True, blank=True)),
                ('customer_message', models.CharField(max_length=100, null=True, blank=True)),
                ('merchant_request_id', models.CharField(max_length=50, null=True, blank=True)),
                ('response_code', models.CharField(max_length=5, null=True, blank=True)),
                ('response_description', models.CharField(max_length=100, null=True, blank=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tbl_online_checkout_requests',
                'verbose_name_plural': 'Online Checkout Requests',
            },
        ),
        migrations.CreateModel(
            name='OnlineCheckoutResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('merchant_request_id', models.CharField(max_length=50, null=True, blank=True)),
                ('checkout_request_id', models.CharField(default=b'', max_length=50)),
                ('result_code', models.CharField(max_length=5, null=True, blank=True)),
                ('result_description', models.CharField(max_length=100, null=True, blank=True)),
                ('mpesa_receipt_number', models.CharField(max_length=50, null=True, blank=True)),
                ('transaction_date', models.DateTimeField(null=True, blank=True)),
                ('phone', models.BigIntegerField(null=True, blank=True)),
                ('amount', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tbl_online_checkout_responses',
                'verbose_name_plural': 'Online Checkout Responses',
            },
        ),
    ]