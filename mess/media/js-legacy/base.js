// base.js

function autoComp( inputId, containerId, searchType, onSelectFunction)
{
    /*
     * Create an autoComplete dropdown list.  Expects to get json
     * in the form of
     *
     *      { results: { id1: name1}, {id2: name2}}}
     * 
     * HTML should have this format:
     *      <div id="someName">
     *          <input id="inputId" />
     *          <div id="containerId" ></div>
     *      </div>
    */
        var schema = ['results', 'name', 'id'];
        var query = '';
        var dataSource = new YAHOO.widget.DS_XHR(query, schema);
        dataSource.scriptQueryParam = 'string';
        dataSource.scriptQueryAppend = 'search=' + searchType;
        dataSource.responseType = YAHOO.widget.DS_XHR.TYPE_JSON; 
        var autoComp = new YAHOO.widget.AutoComplete(
                                        inputId, containerId, dataSource);
        autoComp.forceSelection = true;
        autoComp.allowBrowserAutocomplete = false;
        autoComp.itemSelectEvent.subscribe(onSelectFunction);
} // End fuction autoComp



// These are used for the work history calendar on the account page:

function show_or_hide(id) {
    return function() {
        var elem = document.getElementById(id);
        if (elem.style.display == 'none') {
            elem.style.display = 'block';
        } else {
            elem.style.display = 'none';
        }
    }
}

function attach_hiders(prefix, n) {
    for (i=0; i<n; i++) {
        var hider = document.getElementById(prefix+i+'hider');
        hider.onclick = show_or_hide(prefix+i);
        hider.onclick();
    }
}
