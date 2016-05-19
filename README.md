# RapidAnnotator
The Red Hen Rapid Annotator is a tool for fast and simple classification of items

## Getting started
1. Clone the repository to `your_document_root/annotator`.
2. Setup .htaccess password protection. Not only does this protect your data and you from random annotations. I also have no idea whether the tool is secure, and you probably do not want to find out the hard way.
3. Make sure `json_annotator.cgi` is executable by the web server.
4. Edit `documentation.html` to match your configuration and read it so you can set the appropriate directory permissions.
5. Try it by going to http://YOURSERVER/annotator/annotator.html?dataset=sample&paramset=gender&user=testuser.
