# Scope Of Work

Nautilus WebUI is a SaaS allowing users to select (upload) arbitrary files and obtain a nautilus-made ZIM file of them.

Key Principles

- No authentication, similar to youzim.it
- Cookie-based identification to provide context
- Multiple files can be uploaded at once
- Files are uploaded to S3 (URLs hidden)
- Files are stored for 7d
- Bulk edition of file metadata (title, description, author)
- Automatially create Title metadata from filename
- Read metatadata from known filetypes (PDF, EPUB, docx?) to infer title/desc/author
- Edition of nautilus options (no-random, pagination, show-description, favicon, main-logo, secondary-logo, about)
- Edition of ZIM Metadata
- Limit file uploads to a constant (100MiB for now)
- Build collection.json from the list of files and metadata
- Upload collection.json to S3
- Create a nautilus task to farm.youzim.it
- Receive a webhook on completion
- Inform user with download link
- Send an email if user requested to be informed by email
