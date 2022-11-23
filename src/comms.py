import time
from modbus_tk import modbus_tcp, defines as cst
from helpers import log
from storage import file

PORT = 5020
IP = '0.0.0.0'
SLAVE_NUMBER = 13
RESET_INDEX = 7
BLOCK = "BlockName"

if __name__ == '__main__':

    log.success("[INITIAL] Slave " + str(SLAVE_NUMBER))
    modbusServ = modbus_tcp.TcpServer(PORT, IP, SLAVE_NUMBER)
    modbusServ.start()
    slave_1 = modbusServ.add_slave(SLAVE_NUMBER)
    slave_1.add_block(BLOCK, cst.HOLDING_REGISTERS, 0, 21)
    slave_2 = modbusServ.get_slave(SLAVE_NUMBER)
    
    EquipStat = 1
    LbCount = file.fetchFromFile("lrg_counter")
    SbCount = file.fetchFromFile("sml_counter")
    BSum = SbCount + LbCount
    AlarmLarge = 0
    AlarmSmall = 0
    AlarmSum = 0
    Reset = 0
    Bbmass = 6535
    Sbmass = 6535
    Mbmass = Bbmass + Sbmass
    massSet = 6535
    SetMaxLb = 6535
    SetMaxSb = 6535
    SetMaxBSum = 6535
    
    log.info("[INITIAL] Modbus Server Waiting for client queries...")
    while True:

        # Check counter in file
        sml_new_count = file.fetchFromFile("sml_counter")
        lrg_new_count = file.fetchFromFile("lrg_counter")
        if SbCount != sml_new_count:
            SbCount = sml_new_count
            log.success("[UPDATE] small count has been updated")
        if LbCount != lrg_new_count:
            LbCount = lrg_new_count
            log.success("[UPDATE] large count has been updated")
        BSum = SbCount + LbCount

        # Set Values
        slave_2.set_values(BLOCK, 0, [EquipStat])
        slave_2.set_values(BLOCK, 1, [LbCount])
        slave_2.set_values(BLOCK, 2, [SbCount])
        slave_2.set_values(BLOCK, 3, [BSum])
        slave_2.set_values(BLOCK, 4, [AlarmLarge])
        slave_2.set_values(BLOCK, 5, [AlarmSmall])
        slave_2.set_values(BLOCK, 6, [AlarmSum])
        # slave_2.set_values(BLOCK, 7, [Reset])
        slave_2.set_values(BLOCK, 8, [Bbmass])
        slave_2.set_values(BLOCK, 9, [Sbmass])
        slave_2.set_values(BLOCK, 10, [Mbmass])
        slave_2.set_values(BLOCK, 11, [massSet])
        slave_2.set_values(BLOCK, 12, [SetMaxLb])
        slave_2.set_values(BLOCK, 13, [SetMaxSb])
        slave_2.set_values(BLOCK, 14, [SetMaxBSum])

        # Show Values
        MemMap = [
            EquipStat, LbCount, SbCount, BSum, AlarmLarge, 
            AlarmSmall, AlarmSum, Reset, Bbmass, Sbmass, 
            Mbmass, massSet, SetMaxLb, SetMaxSb, SetMaxBSum
        ]
        log.info("[MEMMAP] {}".format(str(MemMap)))

        # Get Values
        # EquipStat = slave_2.get_values(BLOCK, 0, 1)[0]
        # LbCount = slave_2.get_values(BLOCK, 1, 1)[0]
        # SbCount = slave_2.get_values(BLOCK, 2, 1)[0]
        # BSum = slave_2.get_values(BLOCK, 3, 1)[0]
        # AlarmLarge = slave_2.get_values(BLOCK, 4, 1)[0]
        # AlarmSmall = slave_2.get_values(BLOCK, 5, 1)[0]
        # AlarmSum = slave_2.get_values(BLOCK, 6, 1)[0]
        Reset = slave_2.get_values(BLOCK, 7, 1)[0]
        # Reset = file.fetchFromFile("reset") # for testing only
        # Bbmass = slave_2.get_values(BLOCK, 8, 1)[0]
        # Sbmass = slave_2.get_values(BLOCK, 9, 1)[0]
        # Mbmass = slave_2.get_values(BLOCK, 10, 1)[0]
        # massSet = slave_2.get_values(BLOCK, 11, 1)[0]
        # SetMaxLb = slave_2.get_values(BLOCK, 12, 1)[0]
        # SetMaxSb = slave_2.get_values(BLOCK, 13, 1)[0]
        # SetMaxBSum = slave_2.get_values(BLOCK, 14, 1)[0]

        if Reset == 1 and LbCount != 0:
            file.storeInFile("lrg_counter", 0)
            LbCount = 0
            file.storeInFile("sml_counter", 0)
            SbCount = 0
            BSum = SbCount + LbCount
            log.warn("[UPDATE] large and small counters have been reset")

        time.sleep(0.5)
