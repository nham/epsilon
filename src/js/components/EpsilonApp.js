/** @jsx React.DOM */
var PageList = require('./PageList');
var PageForm = require('./PageForm');
var React = require('react');
var WebStore = require('../WebStore');

var getStateFromStore = function() {
    return {
        data: WebStore.getCurrent()
    };
};

var EpsilonApp = React.createClass({

    getInitialState: function() {
        return getStateFromStore();
    },

    componentDidMount: function() {
        WebStore.addChangeListener(this._onChange);
    },

    componentWillUnmount: function() {
        WebStore.removeChangeListener(this._onChange);
    },

    render: function() {
        return (
            <div className="pageDisplay">
                <PageForm />
                <PageList data={this.state.data} />
            </div>
        );
    },

    _onChange: function() {
        this.setState(getStateFromStore());
    }

});

module.exports = EpsilonApp;
