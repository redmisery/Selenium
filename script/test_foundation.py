import pytest

from page_object import Foundation


class TestFoundation:
    foundation = Foundation()

    @pytest.mark.dependency(scope="session")
    def test01(self):
        pass
