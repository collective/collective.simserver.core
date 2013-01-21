Introduction
=============

The related items is a powerful feature but content managers mostly
(unless they are very committed and know their content very well)
fail to do it, here simserver comes to the rescue and assists in this
task.

collective.simserver.core provides the common core functionality like an
abstracted call interface, training of the corpus  and indexing

Plone communicates with the simserver via HTTP. For the plone products to
work you will also need restsims https://github.com/cleder/restsims which
is a small pyramid wrapper around the Document Similarity Server itself.
Simserver is built on Gensim. Gensim is a free Python framework designed
to automatically extract semantic topics from documents, as efficiently
(computer-wise) and painlessly (human-wise) as possible.


What is a document similarity service?
--------------------------------------

Conceptually, a service that lets you :

* Train a semantic model from a corpus of plain texts (no manual annotation and mark-up needed)
* Index arbitrary documents using this semantic model
* Query the index for similar documents (the query can be either an uid of a document already in the index, or an arbitrary text)

What is it good for?
---------------------

Digital libraries of (mostly) text documents. More generally, it helps
you annotate, organize and navigate documents in a more abstract way,
compared to plain keyword search.

* Enhance the UX by linking content to related content the user might also be interested in
* Easy way to tag documents
* SEO, improve the Page Rank of your site

See also: https://github.com/collective/collective.simserver.related
More information at http://plone.org/products/collective.simserver/

