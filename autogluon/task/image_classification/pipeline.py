import warnings
import logging
import mxnet as mx
from mxnet.gluon import nn
from mxnet import gluon, init, autograd, nd
from mxnet.gluon.data.vision import transforms
from gluoncv.model_zoo import get_model
import gluoncv as gcv
from .metrics import get_metric_instance
from ...core.optimizer import SGD, NAG
from ...core import *
from ...scheduler.resource import get_cpu_count, get_gpu_count
from ...utils import tqdm
from ...utils.mxutils import collect_params
<<<<<<< HEAD
from .nets import get_built_in_network
from .utils import *

from .tricks import *
from ...utils.learning_rate import LR_params
=======
from .nets import get_network
from .utils import *

__all__ = ['train_image_classification']

>>>>>>> origin/master

__all__ = ['train_image_classification']

@args()
def train_image_classification(args, reporter):
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    if args.verbose:
        logger.setLevel(logging.INFO)
        logger.info(args)
<<<<<<< HEAD

    # batch_size & ctx
    target_params = Sample_params(args.batch_size, args.num_gpus, args.num_workers)
    batch_size = target_params.get_batchsize
    ctx = target_params.get_context
=======
    batch_size = args.batch_size * max(args.num_gpus, 1)
    ctx = [mx.gpu(i) for i in range(args.num_gpus)] if args.num_gpus > 0 else [mx.cpu()]

    num_classes = args.dataset.num_classes if hasattr(args.dataset, 'num_classes') else None
    net = get_network(args.net, num_classes, ctx)
    if args.hybridize:
        net.hybridize(static_alloc=True, static_shape=True)
>>>>>>> origin/master

    # params
    target_kwargs = Getmodel_kwargs(ctx,
                                    args.classes,
                                    args.net,
                                    args.tricks.teacher_name,
                                    args.tricks.hard_weight,
                                    args.optimizer.multi_precision,
                                    args.hybridize,
                                    args.tricks.use_pretrained,
                                    args.tricks.use_gn,
                                    args.tricks.last_gamma,
                                    args.tricks.batch_norm,
                                    args.tricks.use_se)
    distillation = target_kwargs.distillation
    net = target_kwargs.get_net
    input_size = net.input_size if hasattr(net, 'input_size') else args.input_size
<<<<<<< HEAD

    if args.tricks.no_wd:
        for k, v in net.collect_params('.*beta|.*gamma|.*bias').items():
            v.wd_mult = 0.0

    if args.tricks.label_smoothing or args.tricks.mixup:
        sparse_label_loss = False
    else:
        sparse_label_loss = True

    if distillation:
        teacher = target_kwargs.get_teacher
        def teacher_prob(data):
            teacher_prob = [nd.softmax(teacher(X.astype(target_kwargs.dtype, copy=False)) / args.tricks.temperature) \
                                for X in data]
            return teacher_prob
        L = gcv.loss.DistillationSoftmaxCrossEntropyLoss(temperature=args.tricks.temperature,
                                                         hard_weight=args.tricks.hard_weight,
                                                         sparse_label=sparse_label_loss)
    else:
        L = gluon.loss.SoftmaxCrossEntropyLoss(sparse_label=sparse_label_loss)
        teacher_prob = None

    # metric
    if args.tricks.mixup:
        metric = get_metric_instance('rmse')
    else:
        metric = get_metric_instance(args.metric)

    # dataloader
    train_data, val_data, batch_fn, num_batches = \
        get_data_loader(args.dataset, input_size, batch_size, args.num_workers, args.final_fit, args.split_ratio)

=======
    train_data, val_data, batch_fn, num_batches = get_data_loader(
            args.dataset, input_size, batch_size, args.num_workers, args.final_fit,
            args.split_ratio)
 
>>>>>>> origin/master
    if isinstance(args.lr_scheduler, str):
        target_lr = LR_params(args.optimizer.lr, args.lr_scheduler, args.epochs, num_batches,
                             args.lr_config.lr_decay_epoch,
                             args.lr_config.lr_decay ,
                             args.lr_config.lr_decay_period,
                             args.lr_config.warmup_epochs,
                             args.lr_config.warmup_lr)
        lr_scheduler = target_lr.get_lr_scheduler
    else:
        lr_scheduler = args.lr_scheduler
    args.optimizer.lr_scheduler = lr_scheduler

<<<<<<< HEAD
    trainer = gluon.Trainer(net.collect_params(), args.optimizer)

    def train(epoch, num_epochs, metric):
=======
    metric = get_metric_instance(args.metric)
    def train(epoch):
>>>>>>> origin/master
        for i, batch in enumerate(train_data):
            metric = default_train_fn(epoch, num_epochs, net, batch, batch_size, L, trainer,
                                      batch_fn, ctx, args.tricks.mixup, args.tricks.label_smoothing,
                                      distillation, args.tricks.mixup_alpha,  args.tricks.mixup_off_epoch,
                                      args.classes,target_kwargs.dtype, metric, teacher_prob)
            mx.nd.waitall()
        return metric

    def test(epoch):
        metric.reset()
        for i, batch in enumerate(val_data):
            default_val_fn(net, batch, batch_fn, metric, ctx, target_kwargs.dtype)

        _, reward = metric.get()

        reporter(epoch=epoch, classification_reward=reward)
        return reward
<<<<<<< HEAD

    tbar = tqdm(range(1, args.epochs + 1))

    for epoch in tbar:

        metric = train(epoch, args.epochs, metric)
        train_metric_name, train_metric_score = metric.get()
        tbar.set_description('[Epoch %d] training: %s=%.3f' %(epoch, train_metric_name, train_metric_score))

=======

    tbar = tqdm(range(1, args.epochs + 1))
    for epoch in tbar:
        train(epoch)
>>>>>>> origin/master
        if not args.final_fit:
            reward = test(epoch)
            tbar.set_description('[Epoch {}] Validation: {:.3f}'.format(epoch, reward))

    if args.final_fit:
        return {'model_params': collect_params(net),
<<<<<<< HEAD
                'num_classes': args.classes}
=======
                'num_classes': num_classes}
>>>>>>> origin/master
