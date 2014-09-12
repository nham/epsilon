/** @jsx React.DOM */
var $ = require('jquery');
var PageList = require('./PageList');
var React = require('react');

var EpsilonApp = React.createClass({

    getInitialState: function() {
        return {data: []};
    },

    loadWebFromServer: function() {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            success: function(data) {
              console.log(data);
              this.setState({data: data});
            }.bind(this),
            error: function(xhr, status, err) {
              console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },

    componentDidMount: function() {
        this.loadWebFromServer();
    },

    render: function() {
        return (
            <div className="pageDisplay">
                <PageList data={this.state.data} />
            </div>
        );
    }

});

module.exports = EpsilonApp;
