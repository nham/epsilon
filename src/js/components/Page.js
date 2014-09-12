/** @jsx React.DOM */
var React = require('react');

var Page = React.createClass({
    render: function() {
        var tagTxt = "";
        for (var i = 0; i < this.props.tags.length; i++) {
            if (i > 0) { tagTxt += ", "; }
            tagTxt += this.props.tags[i];
        }
        return (
            <div className="page">
                <h2 className="pageTitle">
                    {this.props.title}
                </h2>
                <span className="pageTags">
                    {tagTxt}
                </span>
            </div>
        );
    }
});

module.exports = Page;
