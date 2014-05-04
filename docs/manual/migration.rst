Migration to 1.x
================

ElasticSearch 1.x had changed a lot things. This page will help you to migrate to the last version.

Aligned some names with ElasticSearch naming convention:

    StringQuery -> QueryStringQuery


Field Query and FieldParameter are dead. You should update your code from:

    FieldQuery(FieldParameter("name", "+joe"))

to:
    QueryStringQuery(default_field="name", query="+joe"))


CustomScoreQuery is dead. You should update your code from:

    CustomScoreQuery(query=MatchAllQuery(),
        lang="mvel",
        script="_score*(5+doc.position.value)"
    ))

to:

    FunctionScoreQuery(functions=[FunctionScoreQuery.ScriptScoreFunction(
        lang="mvel",
        script="_score*(5+doc.position.value)"
    )])


Custom score query/filter are dead. You should update your code from:

    CustomFiltersScoreQuery.Filter(MatchAllFilter(), 5.0)

to:

    FunctionScoreQuery.BoostFunction(boost_factor=5.0, filter=MatchAllFilter())