from jinja2 import Template
SUMMARY_TEMPLATE = Template("""
Executive Financial Summary (AI Draft)
Period: {{ period_start or 'N/A' }} to {{ period_end or 'N/A' }}

Snapshot:
- Revenue: R{{ '{:,.2f}'.format(revenue) }}
- Expenses: R{{ '{:,.2f}'.format(expenses) }}
- Net Profit: R{{ '{:,.2f}'.format(net_profit) }}
- Avg Daily Net Flow: R{{ '{:,.2f}'.format(avg_daily_net_flow) }}
- Overdraft Days (proxy): {{ overdraft_days }}

Highlights:
{% if top_expenses %}
- Top expense categories: {% for e in top_expenses %}{{e.category}} (R{{ '{:,.0f}'.format(e.total) }}){% if not loop.last %}, {% endif %}{% endfor %}
{% else %}- Expense mix stable with no dominant outliers.
{% endif %}

Risks & Anomalies:
{% if flags %}
{% for f in flags %}- {{ f.type.replace('_',' ').title() }} on {{ f.date }}: R{{ '{:,.2f}'.format(f.amount) }} ({{ f.category }}) - {{ f.description }}
{% endfor %}
{% else %}- No material anomalies detected in the period.
{% endif %}

Recommendations:
- Maintain documentation for high-value transactions flagged above.
- Consider negotiating supplier terms to reduce expense spikes.
- Monitor overdraft usage and interest costs if applicable.
- Validate categorisation for any 'Uncategorized' items and update rules.

Notes:
This summary is system-generated and should be reviewed by a qualified accountant before sign-off.
""")

def build_summary_text(statements, kpis):
    return SUMMARY_TEMPLATE.render(
        period_start=statements.get("period_start"),
        period_end=statements.get("period_end"),
        revenue=statements.get("revenue",0.0),
        expenses=statements.get("expenses",0.0),
        net_profit=statements.get("net_profit",0.0),
        avg_daily_net_flow=kpis.get("avg_daily_net_flow",0.0),
        overdraft_days=kpis.get("overdraft_days",0),
        top_expenses=[type("E",(),e) for e in kpis.get("top_expense_categories",[])],
        flags=kpis.get("flags",[])
    ).strip()
