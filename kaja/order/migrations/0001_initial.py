# Generated by Django 3.0.2 on 2020-02-03 10:50

import core.mixin_model
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurant', '0001_initial'),
        ('menu', '0001_initial'),
        ('address', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_type', models.CharField(choices=[('PCK', 'Pickup'), ('DLV', 'Delivery')], default='DLV', max_length=3)),
                ('delivery_addess', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='address.Address')),
                ('restaurant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='restaurant.Restaurant')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='user.UserProfile')),
                ('variations', models.ManyToManyField(related_name='orders', to='menu.OfferVariation')),
            ],
            bases=(models.Model, core.mixin_model.TimestampMixin),
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_price', models.DecimalField(decimal_places=3, max_digits=10)),
                ('delivery_fee', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=10)),
                ('service_fee', models.DecimalField(decimal_places=3, default=Decimal('0'), max_digits=10)),
                ('payment_type', models.CharField(choices=[('CRD', 'Card Payment'), ('COD', 'Cash on Delivery'), ('COP', 'Cash on Pickup'), ('CRP', 'Card on Pickup')], default='CRD', max_length=3)),
                ('total', models.DecimalField(decimal_places=3, max_digits=10)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='order.Order')),
            ],
            bases=(models.Model, core.mixin_model.TimestampMixin),
        ),
    ]
