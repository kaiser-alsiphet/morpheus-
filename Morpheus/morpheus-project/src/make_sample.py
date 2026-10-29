"""Writes a tiny SYNTHETIC smoke-test dataset (not for reporting metrics). Usage: python -m src.make_sample"""
import pandas as pd
H = ["honestly i just grabbed the bus late and missed half the match, so annoying", "my gran never measured anything, she just tossed flour in till it felt right",
     "we argued about the thermostat again lol, nobody wins that one ever", "cant believe the shop closed, i went there every sunday as a kid",
     "tried fixing the bike myself, ended up with grease everywhere and one spare bolt", "the band was loud and sloppy and honestly the best night out all year"]
A = ["In conclusion, it is important to note that a balanced approach offers numerous benefits for all stakeholders.",
     "Furthermore, leveraging innovative strategies can significantly enhance overall efficiency and drive meaningful outcomes.",
     "Overall, this comprehensive framework provides a robust foundation for sustainable growth and long-term success.",
     "It is essential to consider multiple perspectives when navigating the complex landscape of modern communication.",
     "Additionally, fostering collaboration and transparency plays a pivotal role in achieving optimal results.",
     "Ultimately, understanding these key factors empowers individuals to make informed decisions with confidence."]
items = [(t, 0) for t in H * 3] + [(t, 1) for t in A * 3]
rows = [(f"s{i}", f"{t} (note {i})", l, "synthetic", "human" if l == 0 else "synthetic-ai", f"t{i % 3}", "hand-written sample", f"g{i}")
        for i, (t, l) in enumerate(items)]
pd.DataFrame(rows, columns=["id", "text", "label", "source", "author_or_generator", "topic", "collection_method", "group_id"]).to_csv("data/raw/sample.csv", index=False)
