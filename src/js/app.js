/** @jsx React.DOM */
var React = require('react');
var $ = require('jquery');
var WebStore = require('./WebStore');

var EpsilonApp = require('./components/EpsilonApp');

React.renderComponent(
    <EpsilonApp />,
    document.getElementById('eps_app')
);

var url = "/states";
$.ajax({
    url: url,
    dataType: 'json',
    success: function(data) {
        WebStore.receiveAllStates(data);
    },
    error: function(xhr, status, err) {
        console.error(url, status, err.toString());
    }
});
