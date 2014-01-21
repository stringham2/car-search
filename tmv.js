styles = {}
selector = $('#style-selector')
for(var i=0; i<selector.length; i++) {
  if(selector[i].text.toLowerCase().indexOf('automatic') >= 0) {
    var name = selector[i].text.split(' ')[0];
    if(!styles[name]) {
      styles[name] = selector[i].value
    }
  }
}
styles['default_style'] = styles['LE']
copy(JSON.stringify(styles))