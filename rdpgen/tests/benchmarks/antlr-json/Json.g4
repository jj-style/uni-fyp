grammar Json;

json          : object | array ;
object        : L_BRACE pairs R_BRACE ;
pairs         : pair pairs_tail | ;
pair          : STRING COLON value ;
pairs_tail    : COMMA pairs | ;

value         : STRING | NUMBER | 'true' | 'false' | 'null' | object | array ;
array         : L_BRACKET elements R_BRACKET ;

elements      : value elements_tail | ;
elements_tail : COMMA elements | ;




NUMBER
: '-'? INT '.' [0-9] + | '-'? INT | '-'? INT
;
fragment INT
: '0' | [1-9] [0-9]*
;
COMMA : ',' ;
COLON : ':' ;
L_BRACE: '{' ;
R_BRACE: '}' ;
L_BRACKET : '[' ;
R_BRACKET : ']' ;
WS
: [ \t\n\r] + -> skip
;
STRING
: '"' (.*?) '"' ;
