This is 'pydoctor', an API documentation generator that works by
static analysis.

It was written primarily to replace epydoc for the purposes of the
Twisted project as epydoc has difficulties with zope.interface.  If it
happens to work for your code too, that's a nice bonus :)

pydoctor puts a fair bit of effort into resolving imports and
computing inheritance hierarchies and, as it aims at documenting
Twisted, knows about zope.interface's declaration API and can present
information about which classes implement which interface, and vice
versa.

The default HTML generator requires Twisted.

There are some more notes in the doc/ subdirectory.


Sphinx Integration
------------------

It can link to external API documentation using Sphinx objects inventory using
the following cumulative configuration option::

    --intersphinx=sphinx:http://sphinx.org/objects.inv

All links starting with `sphinx`, (ex: `sphinx.sphinx.addnodes.desc_optional`)
are resolved based on Sphinx index from http://sphinx.org/objects.inv.

It assumes that an inventory contains references for a single root package.

You can add multiple intersphinx options to configure multiple external
project or inventories containing multiple root packages.
