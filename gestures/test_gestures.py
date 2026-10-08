import importlib.machinery
from pathlib import Path
import unittest

router = importlib.machinery.SourceFileLoader('router', str(Path(__file__).with_name('deskflow-gesture'))).load_module()
class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.config={'server_screen':'mac','clients':{'linux':'user@linux'}}
    def test_latest_screen_wins(self):
        self.assertEqual(router.active_screen('switch from "mac" to "linux"\nswitch from "linux" to "mac"'), 'mac')
    def test_disconnect_invalidates_destination(self):
        self.assertIsNone(router.active_screen('switch from "mac" to "linux"\nclient disconnected'))
    def test_remote_is_allowlisted(self):
        self.assertEqual(router.command(self.config,'left','linux')[-3:], ['user@linux','.local/bin/wayland-gesture','left'])
        self.assertIsNone(router.command(self.config,'left','other-client'))
        self.assertIsNone(router.command(self.config,'left',None))
    def test_ssh_option_injection_rejected(self):
        self.config['clients']['linux']='-oProxyCommand=bad'
        with self.assertRaises(ValueError): router.command(self.config,'left','linux')
    def test_local_direction_matches_natural_swipe(self):
        self.assertIn('124', router.command(self.config,'left','mac')[-1])
        self.assertIn('123', router.command(self.config,'right','mac')[-1])
    def test_brightness_release_matches_press(self):
        import configparser
        c=configparser.ConfigParser()
        s=(Path(__file__).parent.parent/'waynergy-config.ini').read_text()
        c.read_string('[main]\n'+s)
        for raw,key_id in [('145','57529'),('146','57528')]:
            self.assertEqual(c['raw-keymap'][raw],c['id-keymap'][key_id])
if __name__=='__main__': unittest.main()
