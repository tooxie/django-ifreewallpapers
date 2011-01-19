//<![CDATA[
window.addEvent('domready', function(){
    var display = $('slide-top-new');
    var elements = display.getElementsByTagName('img');
    var data = new Hash();
    how_many = elements.length;
    for(i=0; i<how_many; i++) {
        var image = elements[i];
        var link = $('a-' + image.name);
        var slide_data = {
            'caption': new String(image.alt),
            'href': new String(link.href)
        };
        var slide = new Hash();
        slide.set(image.src, slide_data);
        data.set(image.src, slide_data);
        // alert(i + ".\ndata {\n    '" + image.name + "': {\n        'caption': " + image.alt + ",\n        'href': " + link + "\n    }\n}");
        // document.getElementById(display.id).removeChild(document.getElementById(image.id));
        // image.dispose();
        // link.dispose();
    }
    slide = slide_data = link = filename = i = image = elements = null;
    display.innerHTML = '';

    var myShow = new Slideshow.KenBurns(
        'slide-top-new',
        data, {
            captions: true,
            height: 400,
            width: 500,
            delay: 4000,
            duration: 1000,
            zoom: 25,
            hu: '',
            loader: false,
            linked: true
        });
});
//]]>
