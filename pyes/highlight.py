# -*- coding: utf-8 -*-

class HighLighter(object):
    """
    This object manage the highlighting

    :arg pre_tags: list of tags before the highlighted text.
        importance is ordered..  ex. ``['<b>']``
    :arg post_tags: list of end tags after the highlighted text.
        should line up with pre_tags.  ex. ``['</b>']``
    :arg fields: list of fields to highlight
    :arg fragment_size: the size of the grament
    :arg number_or_fragments: the maximum number of fragments to
        return; if 0, then no fragments are returned and instead the
        entire field is returned and highlighted.
    :arg fragment_offset: controls the margin to highlight from

    Use this with a :py:class:`pyes.query.Search` like this::

        h = HighLighter(['<b>'], ['</b>'])
        s = Search(TermQuery('foo'), highlight=h)
    """

    def __init__(self, pre_tags=None, post_tags=None, fields=None, fragment_size=None, number_of_fragments=None,
                 fragment_offset=None, encoder=None):
        self.pre_tags = pre_tags
        self.post_tags = post_tags
        self.fields = fields or {}
        self.fragment_size = fragment_size
        self.number_of_fragments = number_of_fragments
        self.fragment_offset = fragment_offset
        self.encoder = encoder

    def add_field(self, name, fragment_size=150, number_of_fragments=3, fragment_offset=None, order="score", type=None):
        """
        Add a field to Highlinghter
        """
        data = {}
        if fragment_size:
            data['fragment_size'] = fragment_size
        if number_of_fragments is not None:
            data['number_of_fragments'] = number_of_fragments
        if fragment_offset is not None:
            data['fragment_offset'] = fragment_offset
        if type is not None:
            data['type'] = type
        data['order'] = order
        self.fields[name] = data

    def serialize(self):
        res = {}
        if self.pre_tags:
            res["pre_tags"] = self.pre_tags
        if self.post_tags:
            res["post_tags"] = self.post_tags
        if self.fragment_size:
            res["fragment_size"] = self.fragment_size
        if self.number_of_fragments:
            res["number_of_fragments"] = self.number_of_fragments
        if self.fragment_offset:
            res["fragment_offset"] = self.fragment_offset
        if self.encoder:
            res["encoder"] = self.encoder
        if self.fields:
            res["fields"] = self.fields
        else:
            res["fields"] = {"_all": {}}
        return res
