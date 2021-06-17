from loguru import logger

from parser.TreeNode import TreeNode
from lexer.TokenType import TokenType
from parser.SyntaxTree import SyntaxTree
from parser.ParseResult import ParseResult
from parser.SyntexParser import SyntexParser


class RecursiveDescentParser(SyntexParser):
    def parse_token_list(self, token_list: list) -> ParseResult:
        result = ParseResult()
        self._token_list = token_list
        if not token_list:
            self._errors.append("No token to read.")
            result.set_errors(self._errors)
            return result
        for token in token_list:
            logger.info(token.to_string())
        result.set_tree(SyntaxTree(self.__program()))
        if self._get_token():
            logger.warning("Source code too long.")
            self._errors.append("Source code too long.")
        if not self._errors:
            logger.debug("语法分析成功")
        else:
            logger.warning("分析完成，存在错误")
        result.set_errors(self._errors)
        return result

    # (1)[Program] -> [ProgramHead] [DeclarePart] [ProgramBody] .
    def __program(self) -> TreeNode:
        root = self._node("Program")
        logger.debug("构造根结点")
        root.set_children(self.__program_head(), self.__declare_part(), self.__program_body(), self._match(TokenType.EOF))
        logger.debug("根结点设置完毕")
        return root

    # (2)[ProgramHead] -> PROGRAM [ProgramName]
    def __program_head(self) -> TreeNode:
        p_head = self._node("ProgramHead")
        logger.debug("构造根结点")
        p_head.set_children(self._match(TokenType.PROGRAM), self.__program_name())
        logger.debug("ProgramHead结点设置完毕")
        return p_head

    # (3)[ProgramName] -> ID
    def __program_name(self) -> TreeNode:
        node = self._node("ProgramName")
        logger.debug("构造ProgramName结点")
        node.set_children(self._match(TokenType.ID))
        logger.debug("ProgramName结点设置完毕")
        return node

    # (4)[DeclarePart] -> [TypeDecPart] [VarDecPart] [ProcDecPart]
    def __declare_part(self) -> TreeNode:
        node = self._node("DeclarePart")
        logger.debug("构造DeclarePart结点")
        node.set_children(self.__type_dec_part(), self.__var_dec_part(), self.__proc_decpart())
        logger.debug("DeclarePart结点设置完毕")
        return node

    # (5)[TypeDecPart] -> ɛ {VAR, PROCEDURE, BEGIN}
    # (6)[TypeDecPart] -> [TypeDec] {TYPE}
    def __type_dec_part(self) -> TreeNode:
        node = self._node("TypeDecPart")
        logger.debug("构造TypeDecPart结点")
        if self._peek_token().get_token_type() in (TokenType.VAR, TokenType.PROCEDURE, TokenType.BEGIN):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.TYPE:
            node.set_children(self.__type_dec())
        else:
            self.error(TokenType.VAR, TokenType.PROCEDURE, TokenType.BEGIN, TokenType.TYPE)
        logger.debug("TypeDecPart结点设置完毕")
        return node

    # (7)[TyprDec] -> type [TypeDecList] {type}
    def __type_dec(self) -> TreeNode:
        node = self._node("TypeDec")
        logger.debug("构造TypeDec结点")
        node.set_children(self._match(TokenType.TYPE), self.__type_dec_list())
        logger.debug("TypeDec结点设置完毕")
        return node

    # (8)[TypeDecList] -> [TypeId] = [TypeDec] ; [TypeDecMore] {ID}
    def __type_dec_list(self) -> TreeNode:
        node = self._node("TypeDecList")
        logger.debug("构造TypeDecList结点")
        node.set_children(self.__type_id(), self._match(TokenType.EQ), self.__type_def(), self._match(TokenType.SEMI), self.__type_dec_more())
        logger.debug("TypeDecList结点设置完毕")
        return node

    # (9) [TypeDecMore] -> ɛ {var, procedure, begin}
    # (10) [TypeDecMore] -> [TypeDecList] {ID}
    def __type_dec_more(self) -> TreeNode:
        node = self._node("typeDefMore")
        logger.debug("构造typeDefMore结点")
        if self._peek_token().get_token_type() in (TokenType.VAR, TokenType.PROCEDURE, TokenType.BEGIN):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.ID:
            node.set_children(self.__type_dec_list())
        else:
            self.error(TokenType.VAR, TokenType.PROCEDURE, TokenType.BEGIN, TokenType.ID)
        logger.debug("typeDefMore结点设置完毕")
        return node

    # (11){TypeId] -> ID {ID}
    def __type_id(self) -> TreeNode:
        node = self._node("TypeID")
        logger.debug("构造TypeID结点")
        node.set_children(self._match(TokenType.ID))
        logger.debug("TypeID结点设置完毕")
        return node

    # (12){TypeDef] -> [BaseType] {integer, char}
    # (13){TypeDef] -> [StructureType] {array, record}
    # (14){TypeDef] -> [ID] {ID}
    def __type_def(self) -> TreeNode:
        node = self._node("TypeDef")
        logger.debug("构造TypeDef结点")
        if self._peek_token().get_token_type() in (TokenType.INTEGER, TokenType.CHAR):
            node.set_children(self.__base_type())
        elif self._peek_token().get_token_type() in (TokenType.ARRAY, TokenType.RECORD):
            node.set_children(self.__structure_type())
        elif self._peek_token().get_token_type() == TokenType.ID:
            node.set_children(self._match(TokenType.ID))
        else:
            self.error(TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID)
        logger.debug("TypeDef结点设置完毕")
        return node

    # (15)[BaseType] -> integer
    # (16)[BaseType] -> char
    def __base_type(self) -> TreeNode:
        node = self._node("BaseType")
        logger.debug("构造BaseType结点")
        if self._peek_token().get_token_type() == TokenType.INTEGER:
            node.set_children(self._match(TokenType.INTEGER))
        elif self._peek_token().get_token_type() == TokenType.CHAR:
            node.set_children(self._match(TokenType.CHAR))
        else:
            self.error(TokenType.INTEGER, TokenType.CHAR)
        logger.debug("BaseType结点设置完毕")
        return node

    # (17)[StructureType] -> [ArrayType] {array}
    # (18)[StructureType] -> [RecType] {record}
    def __structure_type(self) -> TreeNode:
        node = self._node("StructureType")
        logger.debug("构造StructureType结点")
        if self._peek_token().get_token_type() == TokenType.ARRAY:
            node.set_children(self.__array_type())
        elif self._peek_token().get_token_type() == TokenType.RECORD:
            node.set_children(self.__rec_type())
        else:
            self.error(TokenType.ARRAY, TokenType.RECORD)
        logger.debug("StructureType结点设置完毕")
        return node

    # (19)[ArrayType] -> array [ [Low] .. [Top] ] OF [BaseType]
    def __array_type(self) -> TreeNode:
        node = self._node("ArrayType")
        logger.debug("构造ArratType结点")
        node.set_children(
            self._match(TokenType.ARRAY), self._match(TokenType.LMIDPAREN), self.__low(),
            self._match(TokenType.UNDERRANGE), self.__top(), self._match(TokenType.RMIDPAREN),
            self._match(TokenType.OF), self.__base_type()
        )
        logger.debug("ArrayType结点设置完毕")
        return node

    # (20)[Low] -> INTC
    def __low(self) -> TreeNode:
        node = self._node("Low")
        logger.debug("构造Low结点")
        node.set_children(self._match(TokenType.INTC))
        logger.debug("Low结点设置完毕")
        return node

    # (21)[Top] -> INTC
    def __top(self) -> TreeNode:
        node = self._node("Top")
        logger.debug("构造Top结点")
        node.set_children(self._match(TokenType.INTC))
        logger.debug("Top结点设置完毕")
        return node

    # (22)[RecType] -> RECORD [FieldDecList] END
    def __rec_type(self) -> TreeNode:
        node = self._node("RecType")
        logger.debug("构造RecType结点")
        node.set_children(self._match(TokenType.RECORD), self.__filed_dec_list(), self._match(TokenType.END))
        logger.debug("RecType结点设置完毕")
        return node

    # (23)[FiledDecList] -> [BaseType] [Idlist] ; [FiledDecMore] {integer, char}
    # (24)[FiledDecList] -> [ArrayType] [Idlist] ; [FiledDecMore] {array}
    def __filed_dec_list(self) -> TreeNode:
        node = self._node("FiledDecList")
        logger.debug("构造FiledDecList结点")
        if self._peek_token().get_token_type() in (TokenType.INTEGER, TokenType.CHAR):
            node.set_children(self.__base_type(), self.__id_list(), self._match(TokenType.SEMI), self.__filed_dec_more())
        elif self._peek_token().get_token_type() == TokenType.ARRAY:
            node.set_children(self.__array_type(), self.__id_list(), self._match(TokenType.SEMI), self.__filed_dec_more())
        else:
            self.error(TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY)
        logger.debug("FiledDecList结点设置完毕")
        return node

    # (25)[FiledDecMore] -> ɛ {end}
    # (26)[filedDecMore] -> [FiledDecList] {integer, char, array}
    def __filed_dec_more(self) -> TreeNode:
        node = self._node("FiledDecMore")
        logger.debug("构造FiledDecMore结点")
        if self._peek_token().get_token_type() == TokenType.END:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() in (TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY):
            node.set_children(self.__filed_dec_list())
        else:
            self.error(TokenType.END, TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY)
        logger.debug("FiledDecMore结点设置完毕")
        return node

    # (27)[IdList] -> ID [IdMore]
    def __id_list(self) -> TreeNode:
        node = self._node("IdList")
        logger.debug("构造IdList结点")
        node.set_children(self._match(TokenType.ID), self.__id_more())
        logger.debug("IdList结点设置完毕")
        return node

    # (28)[IdMore] -> ɛ {;}
    # (29)[IdMore] -> , [IdList] {,}
    def __id_more(self) -> TreeNode:
        node = self._node("IdMore")
        logger.debug("构造IdMore结点")
        if self._peek_token().get_token_type() == TokenType.SEMI:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.COMMA:
            node.set_children(self._match(TokenType.COMMA), self.__id_list())
        else:
            self.error(TokenType.SEMI, TokenType.COMMA)
        logger.debug("IdMore结点设置完毕")
        return node

    # (30)[VarDecPart] -> ɛ {PROCEDURE, BEGIN}
    # (31)[VarDecPart] -> [VarDec] {VAR}
    def __var_dec_part(self) -> TreeNode:
        node = self._node("VarDecPart")
        logger.debug("构造VarDecPart结点")
        if self._peek_token().get_token_type() in (TokenType.PROCEDURE, TokenType.BEGIN):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.VAR:
            node.set_children(self.__var_dec())
        else:
            self.error(TokenType.PROCEDURE, TokenType.BEGIN, TokenType.VAR)
        logger.debug("VarDecPart结点设置完毕")
        return node

    # (32)[VarDec] -> VAR [VarDecList]
    def __var_dec(self) -> TreeNode:
        node = self._node("VarDec")
        logger.debug("构造VarDec结点")
        node.set_children(self._match(TokenType.VAR), self.__var_dec_list())
        logger.debug("VarDec结点设置完毕")
        return node

    # (33)[VarDecList] -> [TypeDef] [VarIdList] ; [VarDecMore]
    def __var_dec_list(self) -> TreeNode:
        node = self._node("VarDecList")
        logger.debug("构造VarDecList结点")
        node.set_children(self.__type_def(), self.__var_id_list(), self._match(TokenType.SEMI), self.__var_dec_more())
        logger.debug("VarDecList结点设置完毕")
        return node

    # (34)[VarDecMore] -> ɛ {procedure begin}
    # (35)[VarDecMore] -> [VarDecList] {integer char array record id}
    def __var_dec_more(self) -> TreeNode:
        node = self._node("varDecMore")
        logger.debug("构造varDecMore结点")
        if self._peek_token().get_token_type() in (TokenType.PROCEDURE, TokenType.BEGIN):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() in (TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID):
            node.set_children(self.__var_dec_list())
        else:
            logger.error(self._peek_token().get_token_type())
            self.error(TokenType.PROCEDURE, TokenType.BEGIN, TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID)
        logger.debug("VarDecMore结点设置完毕")
        return node

    # (36)[VarIdList] -> ID [VarIdMore]
    def __var_id_list(self) -> TreeNode:
        node = self._node("varIdList")
        logger.debug("构造varIdList结点")
        node.set_children(self._match(TokenType.ID), self.__var_id_more())
        logger.debug("varIdList结点设置完毕")
        return node

    # (37)[VarIdMore] -> ɛ {;}
    # (38)[VarIdMore] -> , [VarIdList] {,}
    def __var_id_more(self) -> TreeNode:
        node = self._node("varIdMore")
        logger.debug("构造varIdMore结点")
        if self._peek_token().get_token_type() == TokenType.SEMI:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.COMMA:
            node.set_children(self._match(TokenType.COMMA), self.__var_id_list())
        else:
            logger.error(self._peek_token().get_token_type())
            self.error(TokenType.SEMI, TokenType.COMMA)
        logger.debug("VarIdMore结点设置完毕")
        return node

    # (39)[ProcDecpart] -> ɛ {begin}
    # (40)[procDecpart] -> [ProcDec[ {procedure}
    def __proc_decpart(self) -> TreeNode:
        node = self._node("ProDecpart")
        logger.debug("构造ProDecpart结点")
        if self._peek_token().get_token_type() == TokenType.BEGIN:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.PROCEDURE:
            node.set_children(self.__proc_dec())
        else:
            self.error(TokenType.BEGIN, TokenType.PROCEDURE)
        logger.debug("ProcDecpart结点设置完毕")
        return node

    # (41)[ProcDec] -> PROCEDURE [ProcName] ( [ParamList] ) ; DecPartInner ProcBody ProcDecMore
    def __proc_dec(self) -> TreeNode:
        node = self._node("ProcDec")
        logger.debug("构造ProcDec结点")
        node.set_children(
            self._match(TokenType.PROCEDURE), self.__proc_name(), self._match(TokenType.LPAREN), self.__param_list(),
            self._match(TokenType.RPAREN), self._match(TokenType.SEMI), self.__dec_part_inner(), self.__proc_body(),
            self.__proc_dec_more()
        )
        logger.debug("ProcDec结点设置完毕")
        return node

    # (42)[ProcDecMore] -> ɛ {begin}
    # (43)[ProcDecMore] -> [ProcDec] {procedure}
    def __proc_dec_more(self) -> TreeNode:
        node = self._node("ProcDecMore")
        logger.debug("构造ProcDecMore结点")
        if self._peek_token().get_token_type() == TokenType.BEGIN:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.PROCEDURE:
            node.set_children(self.__proc_dec())
        else:
            self.error(TokenType.BEGIN, TokenType.PROCEDURE)
        logger.debug("ProcDecMore结点设置完毕")
        return node

    # (44)[ProcName] -> ID
    def __proc_name(self) -> TreeNode:
        node = self._node("ProcName")
        logger.debug("构造ProcName结点")
        node.set_children(self._match(TokenType.ID))
        logger.debug("ProcName结点设置完毕")
        return node

    # (45)[ParamList] -> ɛ {)}
    # (46)[ParamList] -> [ParamDecList] {integer, char, array, record, id, var}
    def __param_list(self) -> TreeNode:
        node = self._node("ParamList")
        logger.debug("构造ParamList结点")
        if self._peek_token().get_token_type() == TokenType.RPAREN:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() in (
            TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID, TokenType.VAR
        ):
            node.set_children(self.__param_dec_list())
        else:
            self.error(TokenType.RPAREN, TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID, TokenType.VAR)
        logger.debug("ParamList结点设置完毕")
        return node

    # (47)[ParamDecList] -> [Param] [ParamMore]
    def __param_dec_list(self) -> TreeNode:
        node = self._node("ParamDecList")
        logger.debug("构造ParamDecList结点")
        node.set_children(self.__param(), self.__param_more())
        logger.debug("ParamDecList结点设置完毕")
        return node

    # (48)[ParamMore] -> ɛ {(}
    # (49)[ParamMore] -> ; [ParamDecList] {;}
    def __param_more(self) -> TreeNode:
        node = self._node("ParamMore")
        logger.debug("构造ParamMore结点")
        if self._peek_token().get_token_type() == TokenType.RPAREN:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.SEMI:
            node.set_children(self._match(TokenType.SEMI), self.__param_dec_list())
        else:
            self.error(TokenType.RPAREN, TokenType.SEMI)
        logger.debug("ParamMore结点设置完毕")
        return node

    # (50)[Param] -> [TypeDef] [FormList] {integer, char, array, record, id}
    # (51)[Param] -> var [TypeDef] [FormList] {var}
    def __param(self) -> TreeNode:
        node = self._node("Param")
        logger.debug("构造Param结点")
        if self._peek_token().get_token_type() in (
            TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID
        ):
            node.set_children(self.__type_def(), self.__form_list())
        elif self._peek_token().get_token_type() == TokenType.VAR:
            node.set_children(self._match(TokenType.VAR), self.__type_def(), self.__form_list())
        else:
            self.error(TokenType.INTEGER, TokenType.CHAR, TokenType.ARRAY, TokenType.RECORD, TokenType.ID, TokenType.VAR)
        logger.debug("Param结点设置完毕")
        return node

    # (52)[FormList] -> ID [FidMore]
    def __form_list(self) -> TreeNode:
        node = self._node("FormList")
        logger.debug("构造FormList结点")
        node.set_children(self._match(TokenType.ID), self.__fid_more())
        logger.debug("FormList结点设置完毕")
        return node

    # (53)[FidMore] -> ɛ {;)}
    # (54)[FidMore] -> , [FormList] {,}
    def __fid_more(self) -> TreeNode:
        node = self._node("FidMore")
        logger.debug("构造FidMore结点")
        if self._peek_token().get_token_type() in (TokenType.SEMI, TokenType.RPAREN):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.COMMA:
            node.set_children(self._match(TokenType.COMMA), self.__form_list())
        else:
            self.error(TokenType.SEMI, TokenType.RPAREN, TokenType.COMMA)
        logger.debug("FidMore结点设置完毕")
        return node

    # (55)[DecPartInner] -> [DeclarePart]
    def __dec_part_inner(self) -> TreeNode:
        node = self._node("ProcDecPart")
        logger.debug("构造ProcDecPart")
        node.set_children(self.__declare_part())
        logger.debug("ProDecPart结点设置完毕")
        return node

    # (56)[ProcBody] -> [ProgramBody] {begin}
    def __proc_body(self) -> TreeNode:
        node = self._node("ProcBody")
        logger.debug("构造ProcBody结点")
        node.set_children(self.__program_body())
        logger.debug("ProcBody结点设置完毕")
        return node

    # (57)[ProgramBody] -> BEGIN [StmList] END {begin}
    def __program_body(self) -> TreeNode:
        node = self._node("ProgramBody")
        logger.debug("构造ProgramBody结点")
        node.set_children(self._match(TokenType.BEGIN), self.__stm_list(), self._match(TokenType.END))
        logger.debug("ProgramBody结点设置完毕")
        return node

    # (58)[StmList] -> [Stm] [StmMore]
    def __stm_list(self) -> TreeNode:
        node = self._node("StmList")
        logger.debug("构造StmList结点")
        node.set_children(self.__stm(), self.__stm_more())
        logger.debug("StmList结点设置完毕")
        return node

    # (59)[StmMore] -> ɛ {else fi end endwh}
    # (60)[StmMore] -> ; [StmList] {;}
    def __stm_more(self) -> TreeNode:
        node = self._node("StmMore")
        logger.debug("构造StmMore结点")
        if self._peek_token().get_token_type() in (TokenType.ELSE, TokenType.FI, TokenType.END, TokenType.ENDWH):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.SEMI:
            node.set_children(self._match(TokenType.SEMI), self.__stm_list())
        else:
            self.error(TokenType.ELSE, TokenType.FI, TokenType.END, TokenType.ENDWH, TokenType.SEMI)
        logger.debug("StmMore结点设置完毕")
        return node

    # (61)[Stm] -> [ConditionalStm] {IF}
    # (62)[Stm] -> [LoopStm] {WHILE}
    # (63)[Stm] -> [InputStm] {READ}
    # (64)[Stm] -> [OutputStm] {WRITE}
    # (65)[Stm] -> [ReturnStm] {RETUEN}
    # (66)[Stm] -> ID [AssCall] {ID}
    def __stm(self) -> TreeNode:
        node = self._node("Stm")
        logger.debug("构造Stm结点")
        if self._peek_token().get_token_type() == TokenType.IF:
            node.set_children(self.__conditional_stm())
        elif self._peek_token().get_token_type() == TokenType.WHILE:
            node.set_children(self.__loop_stm())
        elif self._peek_token().get_token_type() == TokenType.READ:
            node.set_children(self.__input_stm())
        elif self._peek_token().get_token_type() == TokenType.WRITE:
            node.set_children(self.__output_stm())
        elif self._peek_token().get_token_type() == TokenType.RETURN:
            node.set_children(self.__return_stm())
        elif self._peek_token().get_token_type() == TokenType.ID:
            node.set_children(self._match(TokenType.ID), self.__ass_call())
        else:
            self.error(TokenType.IF, TokenType.WHILE, TokenType.READ, TokenType.WRITE, TokenType.RETURN, TokenType.ID)
        logger.debug("Stm结点设置完毕")
        return node

    # (67)[AssCall] -> [AssignmentRest] {:=}
    # (68)[AssCall] -> [CallStmRest] {(}
    def __ass_call(self) -> TreeNode:
        node = self._node("AssCall")
        logger.debug("构造AssCall结点")
        if self._peek_token().get_token_type() in (TokenType.ASSIGN, TokenType.LMIDPAREN, TokenType.DOT):
            node.set_children(self.__assignment_rest())
        elif self._peek_token().get_token_type() == TokenType.LPAREN:
            node.set_children(self.__call_stm_rest())
        else:
            self.error(TokenType.ASSIGN, TokenType.LMIDPAREN, TokenType.DOT, TokenType.LPAREN)
        logger.debug("AssCall结点设置完毕")
        return node

    # (69)[AssignmentRest] -> [VariMore] := [Exp]
    def __assignment_rest(self) -> TreeNode:
        node = self._node("AssignmentRest")
        logger.debug("构造AssignmentRest结点")
        node.set_children(self.__vari_more(), self._match(TokenType.ASSIGN), self.__exp())
        logger.debug("AssignmentRest结点设置完毕")
        return node

    # (70)[ConditionalStm] -> IF [RelExp] THEN [StmList] ELSE [StmList] FI
    def __conditional_stm(self) -> TreeNode:
        node = self._node("ConditionalStm")
        logger.debug("构造ConditionalStm结点")
        node.set_children(
            self._match(TokenType.IF), self.__rel_exp(), self._match(TokenType.THEN), self.__stm_list(),
            self._match(TokenType.ELSE), self.__stm_list(), self._match(TokenType.FI)
        )
        logger.debug("ConditionalStm结点设置完毕")
        return node

    # (71)[LoopStm] -> WHILE [RelExp] DO [StmList] ENDWH
    def __loop_stm(self) -> TreeNode:
        node = self._node("LoopStm")
        logger.debug("构造LoopStm结点")
        node.set_children(self._match(TokenType.WHILE), self.__rel_exp(), self._match(TokenType.DO), self.__stm_list(), self._match(TokenType.ENDWH))
        logger.debug("LoopStm结点设置完毕")
        return node

    # (72)[InputStm] -> READ ( [Invar] )
    def __input_stm(self) -> TreeNode:
        node = self._node("InputStm")
        logger.debug("构造InputStm结点")
        node.set_children(self._match(TokenType.READ), self._match(TokenType.LPAREN), self.__invar(), self._match(TokenType.RPAREN))
        logger.debug("InputStm结点设置完毕")
        return node

    # (73)[Invar] -> ID
    def __invar(self) -> TreeNode:
        node = self._node("Invar")
        logger.debug("构造Invar结点")
        node.set_children(self._match(TokenType.ID))
        logger.debug("Invar结点设置完毕")
        return node

    # (74)[OutputStm] -> WRITE ( [Exp] )
    def __output_stm(self) -> TreeNode:
        node = self._node("OutputStm")
        logger.debug("构造OutputStm结点")
        node.set_children(self._match(TokenType.WRITE), self._match(TokenType.LPAREN), self.__exp(), self._match(TokenType.RPAREN))
        logger.debug("OutputStm结点设置完毕")
        return node

    # (75)[ReturnStm] -> RETURN
    def __return_stm(self) -> TreeNode:
        node = self._node("ReturnStm")
        logger.debug("构造ReturnStm结点")
        node.set_children(self._match(TokenType.RETURN))
        logger.debug("ReturnStm结点设置完毕")
        return node

    # (76)[CallStmRest] -> ( [ActParamList] )
    def __call_stm_rest(self) -> TreeNode:
        node = self._node("CallStmRest")
        logger.debug("构造CallStmRest结点")
        node.set_children(self._match(TokenType.LPAREN), self.__act_param_list(), self._match(TokenType.RPAREN))
        logger.debug("CallStmRest结点设置完毕")
        return node

    # (77)[ActParamList] -> ɛ {)}
    # (78)[ActParamList] -> [Exp] [ActParamMore] {( INTC ID}
    def __act_param_list(self) -> TreeNode:
        node = self._node("ActParamList")
        logger.debug("构造ActParamList结点")
        if self._peek_token().get_token_type() == TokenType.RPAREN:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() in (TokenType.LPAREN, TokenType.INTC, TokenType.ID, TokenType.CHARC):
            node.set_children(self.__exp(), self.__act_param_more())
        else:
            self.error(TokenType.RPAREN, TokenType.LPAREN, TokenType.INTC, TokenType.ID, TokenType.CHARC)
        logger.debug("ActParamList结点设置完毕")
        return node

    # (79)[ActParamMore] -> ɛ {)}
    # (80)[ActParamMore] -> , [ActParamList] {,}
    def __act_param_more(self) -> TreeNode:
        node = self._node("ActParamMore")
        logger.debug("构造ActParamMore结点")
        if self._peek_token().get_token_type() == TokenType.RPAREN:
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.COMMA:
            node.set_children(self._match(TokenType.COMMA), self.__act_param_list())
        else:
            self.error(TokenType.RPAREN, TokenType.COMMA)
        logger.debug("ActParamMore结点设置完毕")
        return node

    # (81)[RelExp] -> [Exp] [OtherRelE]
    def __rel_exp(self) -> TreeNode:
        node = self._node("RelExp")
        logger.debug("构造RelExp结点")
        node.set_children(self.__exp(), self.__other_rel_e())
        logger.debug("RelExp结点设置完毕")
        return node

    # (82)[OtherRelE] -> [CmpOp] [Exp]
    def __other_rel_e(self) -> TreeNode:
        node = self._node("OtherRelE")
        logger.debug("构造OtherRelE结点")
        node.set_children(self.__cmp_op(), self.__exp())
        logger.debug("OtherRelE结点设置完毕")
        return node

    # (83)[Exp] -> [Term] [OtherTerm]
    def __exp(self) -> TreeNode:
        node = self._node("Exp")
        logger.debug("构造Exp结点")
        node.set_children(self.__term(), self.__other_term())
        logger.debug("Exp结点设置完毕")
        return node

    # (84)[OtherTerm] -> ɛ {< = then else fi do endwh ) end ; COMMA}
    # (85)[OtherTerm] -> [AddOp] [Exp] {+ -}
    def __other_term(self) -> TreeNode:
        node = self._node("OtherTerm")
        logger.debug("构造OtherTerm结点")
        if self._peek_token().get_token_type() in (
            TokenType.LT, TokenType.EQ, TokenType.RMIDPAREN, TokenType.THEN, TokenType.ELSE, TokenType.FI, TokenType.DO,
            TokenType.ENDWH, TokenType.RPAREN, TokenType.END, TokenType.SEMI, TokenType.COMMA
        ):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() in (TokenType.PLUS, TokenType.MINUS):
            node.set_children(self.__add_op(), self.__exp())
        else:
            self.error(
                TokenType.LT, TokenType.EQ, TokenType.RMIDPAREN, TokenType.THEN, TokenType.ELSE, TokenType.FI,
                TokenType.DO, TokenType.ENDWH, TokenType.RPAREN, TokenType.END, TokenType.SEMI, TokenType.COMMA,
                TokenType.PLUS, TokenType.MINUS
            )
        logger.debug("OtherTerm结点设置完毕")
        return node

    # (86)[Term] -> [Factor] [OtherFactor]
    def __term(self) -> TreeNode:
        node = self._node("Term")
        logger.debug("构造Term结点")
        node.set_children(self.__factor(), self.__other_factor())
        logger.debug("Term结点设置完毕")
        return node

    # (87)[OtherFactor] -> ɛ { + - < = ] then else fi do endwh ) end ; COMMA}
    # (88)[OtherFactor] -> [MultiOp] [Term] {* /}
    def __other_factor(self) -> TreeNode:
        node = self._node("OtherFactor")
        logger.debug("构造OtherFactor结点")
        if self._peek_token().get_token_type() in (
            TokenType.PLUS, TokenType.MINUS, TokenType.LT, TokenType.EQ, TokenType.RMIDPAREN, TokenType.THEN,
            TokenType.ELSE, TokenType.FI, TokenType.DO, TokenType.ENDWH, TokenType.RPAREN, TokenType.END,
            TokenType.SEMI, TokenType.COMMA
        ):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() in (TokenType.TIMES, TokenType.OVER):
            node.set_children(self.__multi_op(), self.__term())
        else:
            self.error(
                TokenType.PLUS, TokenType.MINUS, TokenType.LT, TokenType.EQ, TokenType.RMIDPAREN, TokenType.THEN,
                TokenType.ELSE, TokenType.FI, TokenType.DO, TokenType.ENDWH, TokenType.RPAREN, TokenType.END,
                TokenType.SEMI, TokenType.COMMA
            )
        logger.debug("OtherFactor结点设置完毕")
        return node

    # (89)[Factor] -> ( [Exp] ) {(}
    # (90)[Factor] -> INTC {INTC}
    # (91)[Factor] -> CHARC {ID}
    # (92)[Factor] -> [Variable] {ID}
    def __factor(self) -> TreeNode:
        node = self._node("Factor")
        logger.debug("构造Factor结点")
        if self._peek_token().get_token_type() == TokenType.LPAREN:
            node.set_children(self._match(TokenType.LPAREN), self.__exp(), self._match(TokenType.RPAREN))
        elif self._peek_token().get_token_type() == TokenType.INTC:
            node.set_children(self._match(TokenType.INTC))
        elif self._peek_token().get_token_type() == TokenType.CHARC:
            node.set_children(self._match(TokenType.INTC))
        elif self._peek_token().get_token_type() == TokenType.ID:
            node.set_children(self.__variable())
        else:
            self.error(TokenType.LPAREN, TokenType.INTC, TokenType.CHARC, TokenType.ID)
        logger.debug("Factor结点设置完毕")
        return node

    # (93)[Variable] -> ID [VariMore]
    def __variable(self) -> TreeNode:
        node = self._node("Variable")
        logger.debug("构造Variable结点")
        node.set_children(self._match(TokenType.ID), self.__vari_more())
        logger.debug("Variable结点设置完毕")
        return node

    # (94)[VariMore] -> ɛ {:= * / + - < = then else fi do endwh ) end ; COMMA}
    # (95)[VariMore] -> [ [Exp] ] {[}
    # (96)[VariMore] -> . [FiledVar] {.}
    def __vari_more(self) -> TreeNode:
        node = self._node("VariMore")
        logger.debug("构造VariMore结点")
        if self._peek_token().get_token_type() in (
            TokenType.ASSIGN, TokenType.TIMES, TokenType.OVER, TokenType.PLUS, TokenType.MINUS, TokenType.LT,
            TokenType.EQ, TokenType.THEN, TokenType.ELSE, TokenType.FI, TokenType.DO, TokenType.ENDWH,
            TokenType.RPAREN, TokenType.END, TokenType.SEMI, TokenType.COMMA, TokenType.RMIDPAREN
        ):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.LMIDPAREN:
            node.set_children(self._match(TokenType.LMIDPAREN), self.__exp(), self._match(TokenType.RMIDPAREN))
        elif self._peek_token().get_token_type() == TokenType.DOT:
            node.set_children(self._match(TokenType.DOT), self.__filed_var())
        else:
            self.error(
                TokenType.ASSIGN, TokenType.TIMES, TokenType.OVER, TokenType.PLUS, TokenType.MINUS, TokenType.LT,
                TokenType.EQ, TokenType.THEN, TokenType.ELSE, TokenType.FI, TokenType.DO, TokenType.ENDWH,
                TokenType.RPAREN, TokenType.END, TokenType.SEMI, TokenType.COMMA, TokenType.RMIDPAREN, TokenType.DOT
            )
        logger.debug("VariMore结点设置完毕")
        return node

    # (97)[FiledVar] -> ID [FiledVarMore]
    def __filed_var(self) -> TreeNode:
        node = self._node("FiledVar")
        logger.debug("构造FiledVar结点")
        node.set_children(self._match(TokenType.ID), self.__filed_var_more())
        logger.debug("FiledVar结点设置完毕")
        return node

    # (98)[FiledVarMore] -> ɛ {:= * / + - < = then else fi do endwh ) end ; COMMA}
    # (99)[filedVarMore] -> [Exp] {[}
    def __filed_var_more(self) -> TreeNode:
        node = self._node("filedVarMore")
        logger.debug("构造filedVarMore结点")
        if self._peek_token().get_token_type() in (
            TokenType.ASSIGN, TokenType.TIMES, TokenType.OVER, TokenType.PLUS, TokenType.MINUS, TokenType.LT,
            TokenType.EQ, TokenType.THEN, TokenType.ELSE, TokenType.FI, TokenType.DO, TokenType.ENDWH,
            TokenType.RPAREN, TokenType.END, TokenType.SEMI, TokenType.COMMA, TokenType.RMIDPAREN
        ):
            node.set_children(self._node_null())
        elif self._peek_token().get_token_type() == TokenType.LMIDPAREN:
            node.set_children(self._match(TokenType.LMIDPAREN), self.__exp(), self._match(TokenType.RMIDPAREN))
        else:
            self.error(
                TokenType.ASSIGN, TokenType.TIMES, TokenType.OVER, TokenType.PLUS, TokenType.MINUS, TokenType.LT,
                TokenType.EQ, TokenType.THEN, TokenType.ELSE, TokenType.FI, TokenType.DO, TokenType.ENDWH,
                TokenType.RPAREN, TokenType.END, TokenType.SEMI, TokenType.COMMA, TokenType.LMIDPAREN
            )
        logger.debug("filedVarMore结点设置完毕")
        return node

    # (100)[CmpOp] -> <
    # (101)[CmpOp] -> =
    def __cmp_op(self) -> TreeNode:
        node = self._node("CmpOp")
        logger.debug("构造CmpOp结点")
        if self._peek_token().get_token_type() == TokenType.LT:
            node.set_children(self._match(TokenType.LT))
        elif self._peek_token().get_token_type() == TokenType.EQ:
            node.set_children(self._match(TokenType.EQ))
        else:
            self.error(TokenType.LT, TokenType.EQ)
        logger.debug("CmpOp结点设置完毕")
        return node

    # (102)[AddOp] -> +
    # (103)[AddOp] -> -
    def __add_op(self) -> TreeNode:
        node = self._node("AddOp")
        logger.debug("构造AddOp结点")
        if self._peek_token().get_token_type() == TokenType.PLUS:
            node.set_children(self._match(TokenType.PLUS))
        elif self._peek_token().get_token_type() == TokenType.MINUS:
            node.set_children(self._match(TokenType.MINUS))
        else:
            self.error(TokenType.PLUS, TokenType.MINUS)
        logger.debug("AddOp结点设置完毕")
        return node

    # (104)[MultiOp] -> *
    # (105)[MultiOp] -> /
    def __multi_op(self) -> TreeNode:
        node = self._node("MultiOp")
        logger.debug("构造MultiOp结点")
        if self._peek_token().get_token_type() == TokenType.TIMES:
            node.set_children(self._match(TokenType.TIMES))
        elif self._peek_token().get_token_type() == TokenType.OVER:
            node.set_children(self._match(TokenType.OVER))
        else:
            self.error(TokenType.TIMES, TokenType.OVER)
        logger.debug("MultiOp结点设置完毕")
        return node
