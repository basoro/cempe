#coding: utf-8
import sys,os
panelPath = '/opt/slemp/server/panel/';
os.chdir(panelPath)
import public

def set_panel_pwd(password):
    import db
    sql = db.Sql()
    result = sql.table('users').where('id=?',(1,)).setField('password',public.md5(password))
    username = sql.table('users').where('id=?',(1,)).getField('username')
    print username;

if __name__ == "__main__":
    type = sys.argv[1];
    if type == 'panel':
        set_panel_pwd(sys.argv[2])
    else:
        print 'ERROR: Parameter error'
