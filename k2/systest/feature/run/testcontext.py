from zaf.component.decorator import requires

from k2.runner.decorator import foreach


@requires(tc='TestContext')
def test_name(tc):
    assert tc.name == 'systest.feature.run.testcontext.test_name', tc.name


@foreach(param=['value'])
@requires(tc='TestContext')
def test_params(tc):
    assert tc.filename_with_params == 'systest.feature.run.testcontext.test_params-param_value', tc.filename_with_params
