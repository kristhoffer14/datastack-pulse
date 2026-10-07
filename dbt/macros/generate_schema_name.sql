-- Override dbt's default behavior, which would name schemas "<target>_<custom>"
-- (e.g. staging_marts). Here the custom schema is used exactly as written.
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}