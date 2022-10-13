import config
from tools import \
    FileManager as Fm, \
    MemoryMapper as Mm, \
    Slave

if __name__ == '__main__':

    print("Set local file to {}/{} \r\n".format(
        config.file.path,
        config.file.name
    ))

    Slave(
        slave_id=config.slave.id,
        block_name=config.slave.block_name,
        refresh_rate=config.slave.refresh_rate,
        port=config.slave.port,
        ip=config.slave.ip,
        file=Fm(
            config.file.path,
            config.file.name
        ),
        mem=Mm()
    ).communicate()
