/** @jsx React.DOM */
var React = require('react');

var Card = React.createClass({
    render: function() {
        return (
            <div key={this.props.id} className="card">
                {this.props.content}
            </div>
        );
    }
});

module.exports = Card;
