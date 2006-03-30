set ai
map x :source ~wam/lib/exrc/xml
map p :source ~wam/lib/exrc/python
map c :source ~wam/lib/exrc/c
" ^Ot for text, mostly for writing flowing text in reports
map t :source ~wam/lib/exrc/spa-report
" Take me to a XXX: or a ZZZ: tag (wam uses these tags to indicate a known
" bug (XXX:) or known missing feature (ZZZ:).)
map z /\([^0-9.]\)\1\1:/
