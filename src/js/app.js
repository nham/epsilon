/** @jsx React.DOM */
var React = require('react');

var EpsilonApp = require('./components/EpsilonApp');

React.renderComponent(
    <EpsilonApp url="/web" />,
    document.getElementById('eps_app')
);
