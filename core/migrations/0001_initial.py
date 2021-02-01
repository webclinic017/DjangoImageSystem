# Generated by Django 3.1.6 on 2021-02-01 19:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductPicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture_src', models.URLField()),
                ('state', models.CharField(default='need_resize', max_length=512)),
                ('small', models.ImageField(blank=True, null=True, upload_to='products/small/')),
                ('medium', models.ImageField(blank=True, null=True, upload_to='products/medium/')),
                ('large', models.ImageField(blank=True, null=True, upload_to='products/large/')),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product_hash', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('pictures', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.productpicture')),
                ('vendor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.vendor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
