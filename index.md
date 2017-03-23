= BookNet
:toc: left
:toclevels: 4
:source-highlighter: pygments 

BookNet is a study of graph properties of books considering characters
as vertices and the interaction between them as edges. The books processed 
are the following:

- [`acts`] from Holy Bible's _Acts_ _of_ _Apostles_.
- [`anna`] Leo Tolstoy's _Anna_ _Karenina_.
- [`arthur`] Bernard Cornwell's _O_ _Rei_ _do_ _Inverno_ - _As_ _crônicas_ _de_ _Artur_, Vol. 1. (King Arthur chronicles)
- [`david`] Charles Dickens' _David_ _Copperfield_.
- [`hawking`] Stephen Hawking's _Minha_ _Breve_ _História_. Editora Intrínseca, 2013.
   https://goo.gl/1p3osS[*Stephen Hawking biography*]
- [`hobbit`] J. R. R. Tolkien's _Hobbit_. Editora Martins Fontes, 2014.
  http://www.isbnsearch.org/isbn/9788578278953[ISBN 9788578278953]
- [`huck`] Mark Twain _Huckleberry_ _Finn_.
- [`luke`] Holy Bible's _Luke_ _Gospel_.
- [`newton`] https://www.goodreads.com/book/show/17098.Isaac_Newton["Isaac Newton, uma biografia"]. James Gleick, Companhia das Letras, 2004, ISBN 8535904646.
- [`pythagoras`] Iamblichus  https://archive.org/details/lifeofpythagoras00iamb[_The_ _Life_ _of_ _Pythagoras_]. Theosophical Publishing House, 1915.
- [`tolkien`]  "J. R. R. Tolkien: o senhor da fantasia". Michael White. DarkSide Books, 2013.
   https://goo.gl/sMWEkl[ISBN 9788566636642]

Holy Bible data was generated using http://goo.gl/NTRhzT[AMERICAN HOLY
BIBLE (ASV) Special Illustrated Edition with Interactive Table of
Contents - Complete Old Testament & New Testament - ASV Bible / ASV
Holy ... - Revised American Standard Version Book 1)].

The data from `anna`, `david`, `homer`, `huck` and were
compiled by Donald E. Knuth for his book
http://www-cs-faculty.stanford.edu/~knuth/sgb.html["Stanford
Graphbase"].

== Core data 

The listed files contain graphs created using the characters as nodes
and the encounters between those characters as edges:

1. http://holanda.xyz/data/booknet/acts.csv[_Acts_ _of_ _Apostles_],
2. http://holanda.xyz/data/booknet/anna.dat[_Anna Karenina_];
3. http://holanda.xyz/data/booknet/arthur.csv[_Arthur_ _chronicles_];
4. http://holanda.xyz/data/booknet/david.dat[_David_ _Copperfield_];
5. http://holanda.xyz/data/booknet/hawking.csv[Hawking biography];
6. http://holanda.xyz/data/booknet/hobbit.csv[_Hobbit_].
7. http://holanda.xyz/data/booknet/huck.dat[_Huckleberry_ _Finn_].
8. http://holanda.xyz/data/booknet/luke.csv[_Luke_ _Gospel_];
9. http://holanda.xyz/data/booknet/newton.csv[Newton biography];
10. http://holanda.xyz/data/booknet/pythagoras.csv[Pythagoras biography];
11. http://holanda.xyz/data/booknet/tolkien.csv[Tolkien biography].

For example, the graph representation

[source,csv]
----
a;b;c
b;"bar baz"
----

means that there are edges `a--b`, `a--c`, `b--c` and `b--"bar baz"`.
All graphs are undirected, and all character names are separated by
semicolon.  When there is space in the character name, quotation marks
surround it.

== Measures

The properties of the vertices (personas) were http://holanda.xyz/data/booknet/booknet.xlsx[*stored in an 
Excel file*]. The measures 
are the following:

1. Frequency;
2. Degree;
3. Betweenness;
4. Closeness;
5. Lobby index.

Information about degree, closeness and betweenness can be found at
https://en.wikipedia.org/wiki/Centrality[Wikipedia]. Lobby index
information can be found in the
http://www.sciencedirect.com/science/article/pii/S0378437113005839[Campiteli's
paper].

== Ranking

The ranking of vertices' degrees also was http://holanda.xyz/data/booknet/rank.xlsx[*stored in an Excel
file*].

== Graph figures

The pictures of the graphs were generated using http://igraph.org/python/[`igraph`].

=== Acts of Apostle

[.float-group]
--
[.center]
[[img-acts]]
.Acts graph.
image::acts.png[align="center"]
--

=== Anna Karenina

* http://holanda.xyz/data/booknet/anna.dat[Index]

[.float-group]
--
[.center]
[[img-anna]]
.Anna Karenina graph.
image::anna.png[align="center"]
--

=== King Arthur

[.float-group]
--
[.center]
[[img-arthur]]
.King Arthur's graph.
image::arthur.png[align="center"]
--

=== David Copperfield

* http://holanda.xyz/data/booknet/david.dat[Index]

[.float-group]
--
[.center]
[[img-david]]
.David Copperfield graph.
image::david.png[align="center"]
--

=== Hawking biography

[.float-group]
--
[.center]
[[img-hawking]]
.Hawking graph.
image::hawking.png[align="center"]
--

=== Hobbit

[.float-group]
--
[.center]
[[img-hobbit]]
.Hobbit graph.
image::hobbit.png[align="center"]
--

=== Huckleberry Finn

* http://holanda.xyz/data/booknet/huck.dat[Index]

[.float-group]
--
[.center]
[[img-huck]]
.Huckleberry Finn graph.
image::huck.png[align="center"]
--

=== Luke gospel

[.float-group]
--
[.center]
[[img-luke]]
.Luke graph.
image::luke.png[align="center"]
--

=== Luke gospel

[.float-group]
--
[.center]
[[img-newton]]
.Newton biography graph.
image::newton.png[align="center"]
--

=== Pythagoras biography

[.float-group]
--
[.center]
[[img-pythagoras]]
.Pythagoras graph.
image::pythagoras.png[align="center"]
--

=== Tolkien biography

[.float-group]
--
[.center]
[[img-tolkien]]
.Tolkien graph.
image::tolkien.png[align="center"]
--

== Source code

Source code of the project is managed using git in the USP repository 
https://git.uspdigital.usp.br/ajholanda/booknet[booknet].