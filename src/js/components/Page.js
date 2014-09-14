/** @jsx React.DOM */
var React = require('react');
var Card = require('./Card');

var Page = React.createClass({
    render: function() {
        var tagTxt = "";
        for (var i = 0; i < this.props.tags.length; i++) {
            if (i > 0) { tagTxt += ", "; }
            tagTxt += this.props.tags[i];
        }

        var cardNodes = [];
        for (id in this.props.cards) {
            var card = this.props.cards[id];
            cardNodes.push(<Card key={card.id}
                                 content={card.content} />);
        }

        return (
            <div className="page">
                <h2 className="pageTitle">
                    {this.props.title}
                </h2>
                <span className="pageTags">
                    {tagTxt}
                </span>
                {cardNodes}
            </div>
        );
    }
});

module.exports = Page;
