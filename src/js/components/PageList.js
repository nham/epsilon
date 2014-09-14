/** @jsx React.DOM */
var Page = require('./Page');
var React = require('react');

var PageList = React.createClass({
    render: function() {
        var pageNodes = [];
        for (id in this.props.data.page_revs) {
            var page = this.props.data.page_revs[id];
            pageNodes.push(<Page key={id} title={page.title} tags={page.tags} />);
        }

        return (
            <div className="pageList">
                {pageNodes}
            </div>
        );
    }
});

module.exports = PageList;
