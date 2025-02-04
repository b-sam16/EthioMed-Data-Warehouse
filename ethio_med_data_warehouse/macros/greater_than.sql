-- macros/greater_than.sql

{% test greater_than(model, column_name, value) %}
    SELECT *
    FROM {{ model }}
    WHERE {{ column_name }} <= {{ value }}
{% endtest %}
