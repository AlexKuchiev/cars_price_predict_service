import pandas as pd
import re
import numpy as np

def column_pars(col):

      torque = []
      max_torque_rpm = []
      regexp = r'([0-9]*[.,]?[0-9]+)'
      for value in col:
          # приводим значения к нижнему регистру и удаляем ','
          value = str(value).lower().replace(',', '')

          if value == 'nan':
            torque.append(None)
            max_torque_rpm.append(None)

          elif 'nm' in value and 'kgm' in value:
            # 0 значение - крутящий момент в Nm
            # 2 значение - обороты
            info = re.findall(regexp, value)
            torque.append(float(info[0]))
            max_torque_rpm.append(float(info[2]))

          elif 'nm' in value:
            if '+' in value:
              # 0 значение - крутящий момент
              # 1 значение - обороты
              # 2 значение - обороты которые надо прибавить к 1 значению
              info = re.findall(regexp, value)

              torque.append(float(info[0]))
              max_torque_rpm.append(float(info[1]) + float(info[2]))

            elif ('-' in value or '~' in value) and '+' not in value:
              # 0 значение - крутящий момент
              # 2 значение -  максимальное значение оборотов
              info = re.findall(regexp, value)

              torque.append(float(info[0]))
              max_torque_rpm.append(float(info[2]))

            else:
              # 0 значение - крутящий момент
              # 1 значение - обороты (может не быть)
              info = re.findall(regexp, value)

              torque.append(float(info[0]))

              if len(info) > 1:
                max_torque_rpm.append(float(info[1]))
              else:
                max_torque_rpm.append(None)

          elif 'kgm' in value:
            if '+' in value:
              # 0 значение - крутящий момент
              # 1 значение - обороты
              # 2 значение - обороты которые надо прибавить к 1 значению
              info = re.findall(regexp, value)

              torque.append(float(info[0]) * 9.8)
              max_torque_rpm.append(float(info[1]) + float(info[2]))

            elif ('-' in value or '~' in value) and '+' not in value:
              # 0 значение - крутящий момент
              # 2 значение -  максимальное значение оборотов
              info = re.findall(regexp, value)

              torque.append(float(info[0]) * 9.8)
              max_torque_rpm.append(float(info[2]))

            else:
              # 0 значение - крутящий момент
              # 1 значение - обороты (может не быть)
              info = re.findall(regexp, value)

              torque.append(float(info[0]) * 9.8)

              if len(info) > 1:
                max_torque_rpm.append(float(info[1]))
              else:
                max_torque_rpm.append(None)
          else:
            # значение в Nm и kgm но без указания единиц измерения
            if '(' in value:
              # 0 значение - крутящий момент в Nm
              # 2 значение - обороты
              info = re.findall(regexp, value)

              torque.append(float(info[0]))
              max_torque_rpm.append(float(info[2]))
            elif '-' in value:
              # 0 значение - крутящий момент
              # 2 значение -  максимальное значение оборотов
              info = re.findall(regexp, value)

              torque.append(float(info[0]))
              max_torque_rpm.append(float(info[2]))
            else:
              # 0 значение - крутящий момент
              # 1 значение - обороты (может не быть)
              info = re.findall(regexp, value)

              torque.append(float(info[0]))
              max_torque_rpm.append(float(info[1]))
      return torque, max_torque_rpm

def process_data(df: pd.DataFrame):
    regexp = r'([0-9]*[.,]?[0-9]+)'

    df['mileage'] = df['mileage'].str.extract(regexp).apply(pd.to_numeric)
    df['engine'] = df['engine'].str.extract(regexp).apply(pd.to_numeric)
    df['max_power'] = df['max_power'].str.extract(regexp).apply(pd.to_numeric)

    torque_train, max_rpm_train = column_pars(df.torque)
    df['torque'] = pd.DataFrame(torque_train)
    df['max_torque_rpm'] = pd.DataFrame(max_rpm_train)
    df = df.fillna(df.median(numeric_only=True))
    df.seats = df.seats.astype(str)
    df['power_per_litr'] = round(df.max_power / (df.engine / 1000), 2)
    df['year'] = df.year ** 2
    df['model'] = df.name.apply(lambda x: x.split()[1])
    df['name'] = df.name.apply(lambda x: x.split()[0])
    df['km_driven_per_year'] = round(df.km_driven / (2023 - df.year ** 0.5), 2)
    df.km_driven = np.log(df.km_driven)
    df.torque = np.log(df.torque)
    df.max_torque_rpm = np.log(df.max_torque_rpm)

    return df
