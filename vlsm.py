from math import log2, ceil
from saving import generate_raport
from copy import deepcopy


class BinNetwork:
    """
    Klasa przetwarzający i umożliwiająca operacje na adresie ip (dodawanie)
    oraz enkapsulująca parametry jej dotyczące.

    Po stworzeniu klasy nalezy wywołać metodę calculate(x) z liczbą hostów dla tej podsieci jako parametr.

    Liczebną interpretację zadresu ip można otrzymać dzięki metodzie calculate_number(x), gdzie parametrem
    jest adres ip w postaci oktetów.
    """

    def __init__(self, address, mask=None):
        """
        Zapisuje adres ip oraz maskę.
        Adres może być listą oktetów.

        :param address: Adres ip
                        np. [192, 168, 1, 0]
                        lub jego liczebna reprezentacja
                        np. 3232235520
        """

        if isinstance(address, int):
            # its a number
            self.as_number = address
        else:
            # assume its a list
            self.as_number = BinNetwork.calculate_number(address)
        if mask:
            # liczona dynamicznie w calculate()
            self.mask = mask  # maska adresu
        self.network = None  # adres ip (BinNetwork)
        self.first_address = None  # pierwszy wolny host
        self.broadcast = None  # broadcast
        self.last_address = None  # ostatni wolny host
        self.allocated_size = None  # Liczba zaalokowanych hostów
        self.hosts = None  # Liczba hostów dla których ta sieć jest przeznaczona

    @classmethod
    def calculate_number(cls, oktets):
        """
        Zamienia adres ip w postaci oktetów na jedną liczbę.

        :param oktets: Oktety adresu ip np. [192.168.1.0]
        :return: Znormalizowana liczba
        """
        s = 0  # the sum
        for oktet in oktets:
            # Dodajemy oktet z lewej strony do liczby, a następnie przesuwamy ją 8 bitów w prawo
            # (Zauważ, że 0 << 8 to nadal zero)
            s = (s << 8) + oktet
        return s

    def calculate_base(self):
        """
        Liczy adres sieci - wszystkie bity hostów są ignorowane (zamieniane na 0).

        :return: BinNumber jako sam adres sieci
        """
        h = pow(2, 32 - self.mask) - 1  # Bity hostów
        s = ~h  # bity adresu sieci
        new_data = self.as_number & s  # Wyłap tylko bity sieci
        return BinNetwork(new_data, self.mask)

    def __str__(self):
        """
        Generuje adres ip jako string

        :return: str
        """
        ans = []
        z = self.as_number
        for _ in range(4):
            ans.append(z & 255)
            z = z >> 8
        ans.reverse()
        return '.'.join(map(str, ans))

    def __repr__(self):
        """
        Generuje podgląd objektów.
        BinNetwork(adres ip, maska)

        :return: podgląd
        """
        return 'BinNetwork({}/{})'.format(self, self.mask)

    def __add__(self, val):
        """
        Dodaj liczbę do adresu ip.
        Według konwencji zwraca nowy objekt BinNetwork

        :param val: Liczba do dodania
        :return: BinNetwork zwiększone o val
        """
        # print('{} + {} = {}'.format(str(self.as_number), val, self.as_number + val))
        return BinNetwork(self.as_number + val, self.mask)

    @property
    def network_with_mask(self):
        """
        :return: string Reprezentacja przedstawiająca adres i maskę
                np. 192.168.1.0/24
        """
        return "{}/{}".format(self.network, self.mask)

    def calculate(self, hosts):
        """
        Wylicza i zapisuje w obiekcie wszystkie parametry sieci:
        self.mask  # maska adresu
        self.network  # adres ip (BinNetwork)
        self.first_address  # pierwszy wolny host
        self.broadcast  # broadcast
        self.last_address  # ostatni wolny host
        self.allocated_size  # Liczba zaalokowanych hostów
        self.hosts  # Liczba hostów dla których ta sieć jest przeznaczona

        :param hosts: Liczba hostów dla których przeznaczona jest ta sieć
        """
        needed_size = hosts + 1
        max_size = 2 ** ceil(log2(needed_size))
        self.mask = 32 - ceil(log2(needed_size))
        network = BinNetwork(self.as_number, self.mask)
        self.network = network
        self.first_address = str(network + 1)
        self.broadcast = network + (max_size - 1)
        self.last_address = network + (max_size - 2)
        self.allocated_size = max_size - 2
        self.hosts = hosts


def validate(default_network, wanted_subnets):
    """
    Weryfikacja wszyskich parametrów wejściowych
    :param default_network: Adres wpisany przez użytkownika
    :param wanted_subnets: Podsieci wpisane przez użytkownika

    Jeżeli nie wygenerowano błędu to zwraca zwalidowane argumenty.
    :return: False, [adres, podsieci]

    Jeżeli wygenerowano błąd to zwraca jego treść.
    :return True, Error

    """
    errors = []  # lista wszyskich błędów
    for x in range(1):
        # wykonaj raz

        # --------------------------- Podsieci --------------------------- #
        try:
            wanted_subnets = [int(sub.strip()) for sub in wanted_subnets.split()]
        except:
            errors.append('Podsieci nie są poprawne')
        if len(wanted_subnets) == 0:
            errors.append('Podaj podsieci')

        if len(errors):
            break
        # --------------------------- Maska --------------------------- #
        mask = None
        for i in range(len(default_network) - 1, -1, -1):
            if default_network[i] in {'/', '\\'}:
                m = default_network[i + 1:]
                try:
                    mask = int(m)
                except ValueError:
                    pass
                default_network = default_network[:i]
                if mask is None:
                    errors.append('Maska nie jest poprawna')
        if mask is None:
            errors.append('Podaj maskę')
            # TODO: niech nie prosi o maskę i samo niech se zrobi.

        if len(errors):
            break
        # --------------------------- Adres ---------------------------#
        # wyciągnięcie adresu nastąpiło podczas sprawdzania maski
        default_network = default_network.split('.')
        if len(default_network) != 4:
            errors.append("Twoja sieć nie posiada 4 oktetów")
        else:
            for oktet in default_network:
                try:
                    if int(oktet) > 255 or int(oktet) < 0:
                        errors.append('Oktety nie mieszczą się w przedziale 0-255')
                except Exception as ex:
                    errors.append('Adres sieci nie jest poprawny')
        if len(errors):
            break
        # --------------------------- rozmiar sieci ---------------------------#
        max_size = 2 ** (32 - mask)

        needed_size = sum([2 ** ceil(log2(sub + 2)) for sub in wanted_subnets])
        # sumuje hosty do zaalokowaniu + 2 z każdej podsieci
        if needed_size > max_size:
            errors.append('Maska nie jest wystarczająca')

    if len(errors):
        # wystąpił błąd. Zwróć pierwszy.
        return True, errors[0]
    else:
        # błędów nie ma.
        new_network = BinNetwork(map(int, default_network), mask)
        # zwraca posortowaną podsieć.
        return False, [new_network, sorted(wanted_subnets, reverse=True)]


def calculate_subnets(default_network, wanted_subnets):
    """
    Generuje wszystkie podsieci dla zadanych hostów zakładając default_network jako
    adres pierwszej podsieci

    W bazowym adresie ignorowane se bity hostów, a pozostawione jedynie bity sieci.

    :param default_network: Sieć zalążek. Musi posiadać maskę
    :param wanted_subnets: Lista podsieci
    :return: Lista podsieci (BitNetwork) o zadanych wielkościach.
    """
    base_network = deepcopy(default_network)
    print(base_network)
    network = base_network.calculate_base()
    print(network)
    # print(repr(network))
    subnets = []
    for hosts in wanted_subnets:
        network.calculate(hosts)  # wygeneruj i zapisz wszystkie możliwe parametry
        subnets.append(network)
        network = network.broadcast + 1  # adres nowej podsieci
    return subnets


def main():
    # test
    network = "192.168.1.255/24"
    want = """100
        50
    """
    error, val = validate(network, want)
    if error:
        print('Wystąpił problem:', val)
    else:
        network, needed_subnets = val
        subnets = calculate_subnets(network, needed_subnets)
        print('Networks: ')
        for x in subnets:
            pass
            print(x.network)
            # generate_raport(network, subnets, 'ans.docx', True)


if __name__ == '__main__':
    main()
