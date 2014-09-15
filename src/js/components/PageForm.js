/** @jsx React.DOM */
var React = require('react');

var PageForm = React.createClass({
    getInitialState: function() {
        return {'visible': false};
    },
    toggleVis: function() {
        this.setState({'visible': !this.state.visible});
    },
    render: function() {
        if (this.state.visible === false) {
            return (<a href="#" onClick={this.toggleVis}>Create new page</a>);
        } else {
            return (
                <div className="pageForm">
                    <input className="title" type="text" placeholder="Title" />
                    <input type="text" placeholder="Tags" />
                    <textarea></textarea>
                    <button>Save</button>
                    <button onClick={this.toggleVis}>Discard</button>
                </div>
            );
        }
    }
});

module.exports = PageForm;
