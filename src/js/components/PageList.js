/** @jsx React.DOM */
var Page = require('./Page');
var React = require('react');

var PageList = React.createClass({
    render: function() {
        var pageNodes = [];
        for (id in this.props.data.page_revs) {
            var page = this.props.data.page_revs[id];
            var tag_names = this.props.data.tags;
            var tags = page.tags.map(function(tid) {
                return tag_names[tid].name;
            });

            var card_data = this.props.data.cards;
            var cards = page.cards.map(function(cid) {
                return {
                    'id': cid,
                    'content': card_data[cid].content
                };
            });

            pageNodes.push(<Page key={id}
                                 title={page.title}
                                 tags={tags}
                                 cards={cards} />);
        }

        return (
            <div className="pageList">
                {pageNodes}
            </div>
        );
    }
});

module.exports = PageList;
