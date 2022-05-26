import serial


def val2str(values: list):
    s = ''
    for value in values:
        s += str(value) + ','
    return s[:-1]


class StageController:
    def __init__(self, port='COM6', baud_rate=9600):
        self.ser = serial.Serial(port, baud_rate)
        self.end = '\r\n'

    def send_recv(self, order: str):
        print(order)
        order += self.end
        self.ser.write(order.encode())
        msg = self.ser.readline().decode()
        msg.strip(self.end)
        print(f'\t-> {msg}')
        return msg

    def get_pos(self):
        order = 'Q:'
        msg = self.send_recv(order)
        pos_list = list(map(int, msg.split(',')))
        return pos_list
        # if msg == 'OK':
        #     return True
        # else:
        #     return False

    def move_rel(self, values: list):
        """

        Args:
            values (list(int)): 各軸の移動量[pulse]を指定．1 pulse あたり 0.01 μm 進む．

        Returns:
            bool (bool): 返答がOKならTrue．

        """

        if len(values) != 3:
            self.close()
            print("move value list must contain three values")
            raise ValueError

        order = 'M:' + val2str(values)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def move_abs(self, values: list):
        """

        Args:
            values (list(int)): 各軸の移動量[pulse]を指定．1 pulse あたり 0.01 μm 進む．

        Returns:
            bool (bool): 返答がOKならTrue．

        """

        if len(values) != 3:
            self.close()
            print('move value list must contain three values')
            raise ValueError

        order = 'A:' + val2str(values)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def move_linear(self, coord: list):
        """

        Args:
            coord (list(int)): 現在位置から見た終点の位置 [pulse]．1 pulse あたり 0.01 μm 進む．

        Returns:
            bool (bool): 返答がOKならTrue．

        """

        if len(coord) != 3:
            self.close()
            print('stop list must contain [axis1(0 or 1), axis2(0 or 1), axis3(0 or 1)]')
            raise ValueError

        order = 'K:' + val2str([1, 2, 3] + coord)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def jog(self, args: list):
        """

        Args:
            args list(int): 各軸の進行方向を1か-1で指定．動かない場合は0．

        Returns:

        """

        if len(args) != 3:
            self.close()
            print('jog list must contain [axis1(0 or 1), axis2(0 or 1), axis3(0 or 1)]')
            raise ValueError
        if args[0] not in [-1, 0, 1] or args[1] not in [-1, 0, 1] or args[2] not in [-1, 0, 1]:
            self.close()
            print('jog value must be -1 ~ 1')
            raise ValueError

        order = 'J:'
        for s in args:
            if s == -1:
                order += '-,'
            elif s == 0:
                order += ','
            elif s == 1:
                order += '+,'
        order = order[:-1] + self.end
        self.ser.write(order.encode())
        return True

    def stop_each(self, args: list):
        """

        Args:
            args (list(int)): 各軸について 0, 1 を指定．1の軸を減速停止する．0は省略可．

        Returns:
            bool (bool): 返答がOKならTrue．

        """

        if len(args) != 3:
            self.close()
            print('stop list must contain [axis1(0 or 1), axis2(0 or 1), axis3(0 or 1)]')
            raise ValueError
        if args[0] not in [0, 1] or args[1] not in [0, 1] or args[2] not in [0, 1]:
            self.close()
            print('stop value must be 0 or 1')
            raise ValueError

        order = 'L:' + val2str(args)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def stop_emergency(self):
        order = 'L:E'
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def set_speed(self, args: list):
        """
        移動速度の指定．
        Args:
            args (list(int)): axis, start, final, rateを指定． axisは設定したい軸で範囲は 1~3．
            start，finalは初速度，最大速度で範囲は 1~4000000 [pulse/s] で 1 pulse あたり 0.01 μm 進む．
            rateは最大速度に到達するまでの時間で範囲は 1~1000 [ms]．

        Returns:
            bool (bool): 返答がOKならTrue．
        """

        if len(args) != 4:
            self.close()
            print('speed list must contain [axis(1~3), start(1~4000000), final(1~4000000), rate(1~1000)]')
            raise ValueError

        axis, start, final, rate = args

        if axis not in [1, 2, 3]:
            self.close()
            print('axis number must be 1 ~ 3')
            raise ValueError
        if start < 1 or 4000000 < start or final < 1 or 4000000 < final or final < start or rate < 1 or 1000 < rate:
            self.close()
            print('speed value out of range.\n1<=slow<=fast<=4000000, 1<=rate<=1000.')
            raise ValueError

        order = 'D:' + val2str(args)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def set_speed_org(self, args: list):
        """
        原点復帰速度の指定．
        Args:
            args (list(int)): axis, start, final, rate, midを指定． axisは設定したい軸で範囲は 1~3．
            start，finalは初速度，最大速度で範囲は 1~4000000 [pulse/s] で 1 pulse あたり 0.01 μm 進む．
            rateは最大速度に到達するまでの時間で範囲は 1~1000 [ms]．
            midは中間速度で範囲は 1~4000000 [pulse/s] で 1 pulse あたり 0.01 μm 進む．

        Returns:
            bool (bool): 返答がOKならTrue
        """

        if len(args) != 5:
            self.close()
            print('speed list must contain [axis(1~3), start(1~4000000), final(1~4000000), rate(1~1000), mid(1~4000000)]')
            raise ValueError

        axis, start, final, rate, mid = args

        if axis not in [1, 2, 3]:
            self.close()
            print('axis number must be 1 ~ 3')
            raise ValueError
        if start < 1 or 4000000 < start or final < 1 or 4000000 < final or mid < start or final < mid or rate < 1 or 1000 < rate:
            self.close()
            print('speed value out of range.\n1<=slow<=mid<=fast<=4000000, 1<=rate<=1000.')
            raise ValueError

        order = 'B:' + val2str(args)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def go_machine_org(self, args: list):
        """

        Args:
            args (list(int)): 各軸について 0, 1 を指定．1の軸を機械原点復帰する．0は省略可．

        Returns:
            bool (bool): 返答がOKならTrue．

        """

        if len(args) != 3:
            self.close()
            print('go org list must contain [axis1(0 or 1), axis2(0 or 1), axis3(0 or 1)]')
            raise ValueError
        if args[0] not in [0, 1] or args[1] not in [0, 1] or args[2] not in [0, 1]:
            self.close()
            print('go org value must be 0 or 1')
            raise ValueError

        order = 'H:' + val2str(args)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def go_logical_org(self):
        pos = self.get_pos()
        coord = list(map(lambda x: -x, pos))
        self.move_linear(coord)

    def set_logical_org(self, args: list):
        """

        Args:
            args (list(int)): 各軸について 0, 1 を指定．1の軸を論理原点設定する．0は省略可．

        Returns:
            bool (bool): 返答がOKならTrue．

        """

        if len(args) != 3:
            self.close()
            print('set logical org list must contain [axis1(0 or 1), axis2(0 or 1), axis3(0 or 1)]')
            raise ValueError
        if args[0] not in [0, 1] or args[1] not in [0, 1] or args[2] not in [0, 1]:
            self.close()
            print('set logical org value must be 0 or 1')
            raise ValueError

        order = 'R:' + val2str(args)
        msg = self.send_recv(order)
        if msg == 'OK':
            return True
        else:
            return False

    def close(self):
        self.ser.close()
        print('closed')
        return True
