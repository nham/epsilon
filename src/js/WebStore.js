var EventEmitter = require('events').EventEmitter;
var merge = require('react/lib/merge');

var change_event = 'change';

var _states = {};
var _curr_id = -1;

var WebStore = merge(EventEmitter.prototype, {
    emitChange: function() {
        this.emit(change_event)
    },

    addChangeListener: function(callback) {
        this.on(change_event, callback);
    },

    removeChangeListener: function(callback) {
        this.removeListener(change_event, callback);
    },

    getCurrent: function() {
        var curr = {};
        if (!('states' in _states)) {
            return curr;
        } else {
            curr['page_revs'] = _states['states'][_curr_id]['page_revs'];
        }
        if ('cards' in _states) {
            curr['cards'] = _states['cards'];
        }
        if ('tags' in _states) {
            curr['tags'] = _states['tags'];
        }
        return curr;
    },

    // According to Flux, we should not have this since it is a "setter"
    // in the public API of WebStore. This might only stick around
    // temporarily; it depends on whether setting up a dispatcher seems
    // like it's worth the trouble.
    receiveAllStates: function(data) {
        _states['cards'] = data['cards'];
        _states['tags'] = data['tags'];
        _curr_id = data['curr_state'];

        if(!('states' in _states)) {
            _states['states'] = {};
        }

        for(id in data['states']) {
            var state = data['states'][id];
            if (!_states['states'][state.id]) {
                _states['states'][state.id] = state;
            }
        }

        this.emitChange();
    },

});

module.exports = WebStore;
