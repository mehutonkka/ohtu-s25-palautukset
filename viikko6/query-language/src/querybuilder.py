from matchers import And, Or, Not, PlaysIn, HasAtLeast, HasFewerThan, All


class QueryBuilder:
    def __init__(self, matcher=None):
        self._matcher = matcher if matcher is not None else All()

    def one_of(self, *matchers):
        built = []
        for m in matchers:
            if isinstance(m, QueryBuilder):
                built.append(m.build())
            else:
                built.append(m)

        return QueryBuilder(Or(*built))

    def plays_in(self, team):
        return QueryBuilder(And(self._matcher, PlaysIn(team)))

    def has_at_least(self, value, attr):
        return QueryBuilder(And(self._matcher, HasAtLeast(value, attr)))

    def has_fewer_than(self, value, attr):
        return QueryBuilder(And(self._matcher, HasFewerThan(value, attr)))

    def build(self):
        return self._matcher
