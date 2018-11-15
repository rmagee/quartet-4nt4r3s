from gs123.conversion import BarcodeConverter


class AntaresBarcodeConverter(BarcodeConverter):
    '''
    Adds an extra property to return a serial number (with 0 padding)
    and the extension digit at the beginning if it's an SSCC.
    '''
    @property
    def extension_prepended_serial_number_field(self) -> str:
        """
        Returns the serial number with 0s if applicable, and
        an extension digit (for SSCC)
        """
        ext = self.extension_digit or ''
        return str(ext) + self.serial_number_field
