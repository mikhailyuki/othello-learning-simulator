from typing import List
from random import random


class OthelloBoard:
    """
    オセロの盤面情報の保持と各種処理を行うクラス。

    :param my_stone: 自分の石の位置
    :type my_stone: int
    :param your_stone: 相手の石の位置
    :type your_stone: int
    :param now_turn: 現在の手番
    :type now_turn: int
    """

    def __init__(self,
                 my_stone: int = 0x00_00_00_08_10_00_00_00,
                 your_stone: int = 0x00_00_00_10_08_00_00_00,
                 now_turn: bool = True,):
        self.my_stone: int = my_stone
        self.your_stone: int = your_stone
        self.now_turn: bool = now_turn

    def can_put(self, put: int) -> bool:
        """
        指定された位置に石を置けるかどうかを判定する関数。

        :param put: 置こうとしている石の位置
        :type put: int
        :return: 指定された位置が合法手であればTrue、そうでなければFalse
        :rtype: bool
        """
        # 合法手の位置を取得
        legal_board: int = self.get_legal_board()

        return put & legal_board == put

    def reverse(self, put: int) -> bool:
        """
        指定された位置に石を置き、盤面の反転処理を行う関数。

        :param put: 石を置く位置
        :type put: int
        :return: 指定された位置が合法手であればTrue、そうでなければFalse
        :rtype: bool
        """
        # 指定された位置が合法手でなければFalseを返す
        if not self.can_put(put):
            return False

        # 反転する石の位置
        rev: int = 0

        for k in range(8):
            mask: int = self.transfer(put, k)
            tmp_rev: int = 0
            while mask & self.your_stone != 0:
                tmp_rev |= mask
                mask = self.transfer(mask, k)
            if mask & self.my_stone != 0:
                rev |= tmp_rev

        # 石を反転
        self.my_stone ^= put | rev
        self.your_stone ^= rev

        return True

    def reversed(self, put: int) -> 'OthelloBoard':
        """
        指定された位置に石を置き、反転処理を行った盤面を返す関数。

        :param put: 石を置く位置
        :type put: int
        :return: 反転処理をした盤面
        :rtype: OthelloBoard
        """
        # 新たにOthelloBoardのインスタンスを生成し、盤面の反転処理を行う
        reversed_board: OthelloBoard = OthelloBoard(self.my_stone, self.your_stone, self.now_turn)
        reversed_board.reverse(put)

        return reversed_board

    def transfer(self, put: int, k: int) -> int:
        """
        reverse()で反転する石を探索するための関数。

        :param put: 現在着目しているマスの位置
        :type put: int
        :param k: 探索方向
        :type k: int
        :return: 反転する石の位置にビットが立っている整数
        :rtype: int
        """
        if k == 0:
            return (put << 8) & 0x00_ff_ff_ff_ff_ff_ff_00
        elif k == 1:
            return (put << 7) & 0x00_7e_7e_7e_7e_7e_7e_00
        elif k == 2:
            return (put >> 1) & 0x7e_7e_7e_7e_7e_7e_7e_7e
        elif k == 3:
            return (put >> 9) & 0x00_7e_7e_7e_7e_7e_7e_00
        elif k == 4:
            return (put >> 8) & 0x00_ff_ff_ff_ff_ff_ff_00
        elif k == 5:
            return (put >> 7) & 0x00_7e_7e_7e_7e_7e_7e_00
        elif k == 6:
            return (put << 1) & 0x7e_7e_7e_7e_7e_7e_7e_7e
        elif k == 7:
            return (put << 9) & 0x00_7e_7e_7e_7e_7e_7e_00
        else:
            return 0

    def get_stone(self) -> (int, int):
        """
        現在の盤面における石の位置を(黒, 白)の形式で返す。

        :return: 石の位置
        :rtype: (int, int)
        """
        black_stone = self.my_stone if self.now_turn else self.your_stone
        white_stone = self.your_stone if self.now_turn else self.my_stone

        return black_stone, white_stone

    def get_legal_board(self, my_stone: int = None, your_stone: int = None) -> int:
        """
        与えられた盤面における合法手の位置を返す関数。
        引数が渡されなかった場合、メンバ変数の値がそのまま使われる。

        :param my_stone: 自分の石の位置
        :type my_stone: Optional[int]
        :param your_stone: 相手の石の位置
        :type your_stone: Optional[int]
        :return: 合法手の位置
        :rtype: int
        """
        # 引数が与えられなかった場合、メンバ変数のmy_stoneとyour_stoneがそのまま使われる
        if my_stone is None:
            my_stone = self.my_stone
        if your_stone is None:
            your_stone = self.your_stone

        # 左右端の番兵
        horizontal_sentinel: int = your_stone & 0x7e_7e_7e_7e_7e_7e_7e_7e
        # 上下端の番兵
        vertical_sentinel: int = your_stone & 0x00_ff_ff_ff_ff_ff_ff_00
        # 全辺の番兵
        all_side_sentinel: int = your_stone & 0x00_7e_7e_7e_7e_7e_7e_00
        # 空きマス
        blank_board: int = ~(my_stone | your_stone)
        # 隣接マスに相手の石があるかどうかを調べるための一時変数
        tmp: int
        # 合法手
        legal_board: int

        # 8方向を順に探索
        # 左
        tmp = horizontal_sentinel & (my_stone << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        legal_board = blank_board & (tmp << 1)

        # 右
        tmp = horizontal_sentinel & (my_stone >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        legal_board |= blank_board & (tmp >> 1)

        # 上
        tmp = vertical_sentinel & (my_stone << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        legal_board |= blank_board & (tmp << 8)

        # 下
        tmp = vertical_sentinel & (my_stone >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        legal_board |= blank_board & (tmp >> 8)

        # 左上
        tmp = all_side_sentinel & (my_stone << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        legal_board |= blank_board & (tmp << 9)

        # 右上
        tmp = all_side_sentinel & (my_stone << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        legal_board |= blank_board & (tmp << 7)

        # 左下
        tmp = all_side_sentinel & (my_stone >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        legal_board |= blank_board & (tmp >> 7)

        # 右下
        tmp = all_side_sentinel & (my_stone >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        legal_board |= blank_board & (tmp >> 9)

        return legal_board

    def get_legal_list(self) -> List[int]:
        """
        現在の盤面における合法手の位置を格納したリストを返す関数。

        :return: 合法手の位置を格納したリスト
        :rtype: List[int]
        """
        # 全ての合法手の位置を表すビット
        legal_board: int = self.get_legal_board()
        # 合法手の位置を格納するリスト
        legal_list: List[int] = []
        # マスク用の変数 左上から右下まで順に1ビットずつ遷移していく
        mask: int = 0x80_00_00_00_00_00_00_00
        for i in range(64):
            if legal_board & (mask >> i) != 0:
                legal_list.append(mask >> i)

        return legal_list

    def print_board(self):
        """
        与えられた盤面をコンソールに出力する関数。
        TODO あくまでCUI用の関数なので削除予定

        """
        # 合法手の位置
        legal_board: int = self.get_legal_board()
        # マスク用の変数 左上から右下まで順に1ビットずつ遷移していく
        mask: int = 0x80_00_00_00_00_00_00_00
        # 黒石と白石の位置
        black_stone: int
        white_stone: int
        # 手番によってmy_stoneとyour_stoneのどちらを参照するかが変わる
        if self.now_turn:
            black_stone = self.my_stone
            white_stone = self.your_stone
        else:
            black_stone = self.your_stone
            white_stone = self.my_stone

        for i in range(8):
            for j in range(8):
                tmp_mask: int = mask >> (i * 8 + j)
                if black_stone & tmp_mask > 0:
                    print('●', end='')
                elif white_stone & tmp_mask > 0:
                    print('○', end='')
                elif legal_board & tmp_mask > 0:
                    print('※', end='')
                else:
                    print('　', end='')
            print('')

    def change_turn(self):
        """
        手番の交代処理を行う関数。

        """
        self.my_stone, self.your_stone = self.your_stone, self.my_stone
        self.now_turn = not self.now_turn

    def is_end(self) -> bool:
        """
        終局判定を行う関数。

        :return: 互いに合法手が存在しなければTrueを返す
        :rtype: bool
        """
        flag1 = self.get_legal_board(self.your_stone, self.my_stone)
        flag2 = self.get_legal_board()

        return flag1 == 0 and flag2 == 0

    def judge(self) -> int:
        """
        勝敗判定を行う関数。

        :return: 自分の勝利なら1、相手の勝利なら-1、引き分けなら0を返す
        :rtype: int
        """
        # 石の数
        my_stone_count: int = bin(self.my_stone).count('1')
        your_stone_count: int = bin(self.your_stone).count('1')

        if my_stone_count > your_stone_count:
            return 1
        elif your_stone_count > my_stone_count:
            return -1
        else:
            return 0


class ArtificialIntelligence:
    """
    オセロAIの思考を司るクラス。

    :param think_depth: AIの読みの深さ
    :type think_depth: int
    """

    def __init__(self, think_depth: int):
        self.think_depth: int = think_depth

    def random(self, now_board: 'OthelloBoard') -> int:
        """
        与えられた盤面における合法手からランダムに一手選び、それを返す関数。

        :param now_board: 盤面の情報
        :type now_board: OthelloBoard
        :return: 合法手からランダムに選んだ手(合法手がなければ-1を返す)
        :rtype: int
        """
        # 合法手の位置を格納したリスト
        legal_list: List[int] = now_board.get_legal_list()
        # 合法手がなければ-1を返し、パスとみなす
        if len(legal_list) == 0:
            return -1
        # リストの範囲内でランダムにインデックスを選ぶ
        random_num: int = random.randrange(0, len(legal_list))

        return legal_list[random_num]

    def evaluate_board(self, now_board: 'OthelloBoard') -> int:
        """
        与えられた盤面の評価値を返す関数。

        :param now_board: 盤面の情報
        :type now_board: OthelloBoard
        :return: 盤面の評価値
        :rtype: int
        """
        # 自分の石の個数
        my_stone_count: int = bin(now_board.my_stone).count('1')
        # 相手の石の個数
        your_stone_count: int = bin(now_board.your_stone).count('1')

        return my_stone_count - your_stone_count

    def nega_alpha(self, now_depth: int, now_board: 'OthelloBoard', alpha: int, beta: int) -> (int, int):
        """
        ネガアルファ法で最善手を探索する関数。

        :param now_depth: 現在の探索の深さ。上限(think_depth)に達したら盤面評価を行う。
        :type now_depth: int
        :param now_board: 現在の盤面。
        :type now_board: OthelloBoard
        :param alpha: 評価値の下限。子ノードから帰ってきた評価値とmaxをとり、betaを超えたら枝刈りする。
        :type alpha: int
        :param beta:評価値の上限。alphaがこの値を超えた時点でこのノードを探索する必要がなくなる。
        :type beta: int
        :return: 評価値と最善手。
        :rtype: (int, int)
        """
        best_put: int = -1

        # 探索木の末端か終局まで到達したら、盤面の評価値にマイナスをかけた値を返す
        if now_depth == self.think_depth or now_board.is_end():
            value: int = self.evaluate_board(now_board)
            return -value, best_put

        # 合法手のリストを取得する
        legal_list: List[int] = now_board.get_legal_list()
        # 合法手が存在しなければパスして次の手番へ
        if len(legal_list) == 0:
            # 新たに盤面のインスタンスを生成し、手番の交代処理を行う
            next_board: OthelloBoard = OthelloBoard(now_board.my_stone, now_board.your_stone)
            next_board.change_turn()
            # 子ノードの評価値を再帰で取得する(alphaとbetaの値はそのまま渡す)
            child_value, _ = self.nega_alpha(now_depth + 1, next_board, alpha, beta)
            # alphaの更新を行う
            alpha = max(alpha, child_value)
            return -alpha, best_put

        # 合法手全てに枝を張る
        for legal_put in legal_list:
            # 石の反転処理がされた盤面のインスタンスを生成し、手番の交代処理を行う
            next_board: OthelloBoard = now_board.reversed(legal_put)
            next_board.change_turn()
            # 子ノードの評価値を再帰で取得する
            child_value, _ = self.nega_alpha(now_depth + 1, next_board, -beta, -alpha)
            # 子ノードの評価値がalpha(下限)を超えていればalphaを更新し、現在着目している手を最善手とする
            if child_value > alpha:
                alpha = child_value
                best_put = legal_put
            # alphaがbetaを超えた場合このノードを探索する必要がなくなるため、枝刈りをする
            if alpha >= beta:
                return -alpha, best_put

        # 現在のノードの評価値と最善手を返す
        if now_depth == 0:
            return alpha, best_put
        else:
            return -alpha, best_put
