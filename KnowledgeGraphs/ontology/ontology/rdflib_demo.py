from rdflib import Graph, RDF
from rdflib.compare import isomorphic

from export_results import HERE, NS, run


def main():
    ontologies = HERE / "output" / "ontologies"
    asserted = Graph().parse(ontologies / "lol_full.owl", format="xml")
    print(f"Loaded lol_full.owl (RDF/XML): {len(asserted)} triples")

    abilities = sorted(asserted.objects(NS.Lux, NS.hasAbility))
    assert set(abilities) == {NS[f"Lux_{slot}"] for slot in ("P", "Q", "W", "E", "R")}
    print("Lux abilities:", ", ".join(str(ability).removeprefix(str(NS)) for ability in abilities))

    excerpt = Graph()
    excerpt.bind("lol", NS)
    for pattern in (
        (NS.Lux, RDF.type, NS.Champion),
        (NS.Lux, NS.hasAbility, NS.Lux_W),
        (NS.Lux_W, NS.hasEffect, NS.Lux_W_Shield_Ally),
        (NS.Lux_W_Shield_Ally, None, None),
    ):
        for triple in asserted.triples(pattern):
            excerpt.add(triple)
    assert (NS.Lux_W, NS.hasEffect, NS.Lux_W_Shield_Ally) in excerpt
    assert (NS.Lux_W_Shield_Ally, NS.hasTargetType, NS.Ally) in excerpt
    turtle = excerpt.serialize(format="turtle")
    assert isomorphic(excerpt, Graph().parse(data=turtle, format="turtle"))
    print("\nLux W excerpt (Turtle):")
    print(turtle.strip())
    print("Turtle round trip: PASS")

    rows = list(run(asserted, "01_competency_question.rq"))
    names = {row.champion for row in rows}
    assert names == {NS.Karma, NS.Lux, NS.Morgana} and len(rows) == 7
    print("\nCompetency question: Karma, Lux, Morgana; 7 explanation rows")
    for row in rows:
        ability_ids = [str(term).removeprefix(str(NS)) for term in (
            row.shieldAbility, row.controlAbility, row.controlMechanic,
        )]
        print("  " + " | ".join(ability_ids))

    materialized = Graph().parse(ontologies / "lol_full_inferred.owl", format="xml")
    for label, graph, expected in (("Asserted", asserted, set()), ("HermiT materialized", materialized, names)):
        matches = {row.champion for row in run(graph, "03_inferred_class.rq")}
        has_inverse = (NS.Lux_Q, NS.isAbilityOf, NS.Lux) in graph
        assert matches == expected and has_inverse == bool(expected)
        print(f"{label}: {len(matches)} SupportControlMage instances; Lux_Q isAbilityOf Lux = {has_inverse}")


if __name__ == "__main__":
    main()
